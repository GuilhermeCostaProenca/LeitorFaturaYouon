# main.py

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import json
import fitz

from extractor.parser import parse_basic_energy_info
from extractor.parser_enel import parse_enel
from extractor.parser_energisa_mg import parse_energisa_mg 
from extractor.parser_energisa_ms import parse_energisa_ms
from extractor.parser_equatorial import parse_equatorial

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def detect_distribuidora(text):
    text_upper = text.upper()
    if "ENEL" in text_upper:
        return "enel"
    elif "ENERGISA MINAS RIO" in text_upper:
        return "energisa_mg"
    elif "ENERGISA MATO GROSSO DO SUL" in text_upper:
        return "energisa_ms"
    elif "ENERGISA" in text_upper:
        return "energisa"
    elif "EQUATORIAL" in text_upper:
        return "equatorial"
    else:
        return "generico"

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
    distribuidora = detect_distribuidora(text)

    if distribuidora == "enel":
        result = parse_enel(text)
    elif distribuidora == "energisa_mg":
        result = parse_energisa_mg(text)
    elif distribuidora == "energisa_ms":
        result = parse_energisa_ms(text)
    elif distribuidora == "equatorial":
        result = parse_equatorial(text)
    else:
        result = parse_basic_energy_info(text)
        result["distribuidora_detectada"] = "Desconhecida"
        result["precisa_revisao"] = True

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    Path("logs").mkdir(exist_ok=True)
    with open(f"logs/{timestamp}_raw.txt", "w", encoding="utf-8") as f:
        f.write(text)
    with open(f"logs/{timestamp}_log.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    Path(temp_path).unlink()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "data": result,
        "alerta": result.get("precisa_revisao", False)
    })