from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import fitz
from pathlib import Path
from datetime import datetime
import json

from extractor.parser import parse_basic_energy_info

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(temp_path)
    result = parse_basic_energy_info(text)

    # LOGS AUTOMÁTICOS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    Path("logs").mkdir(exist_ok=True)

    with open(f"logs/{timestamp}_raw.txt", "w", encoding="utf-8") as f:
        f.write(text)

    with open(f"logs/{timestamp}_log.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    Path(temp_path).unlink()

    return templates.TemplateResponse("index.html", {"request": request, "data": result})
