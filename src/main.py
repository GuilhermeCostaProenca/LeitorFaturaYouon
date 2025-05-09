import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.azure_reader import extrair_texto_azure
from parser_dispatcher import parser_dispatcher
from src.validador import validar_dados


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, fatura: UploadFile = File(...)):
    if not fatura.filename.lower().endswith(".pdf"):
        return templates.TemplateResponse("index.html", {"request": request, "erro": "Formato inválido. Envie um PDF."})

    caminho = f"temp/{fatura.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(caminho, "wb") as buffer:
        buffer.write(await fatura.read())

    try:
        texto_extraido = extrair_texto_azure(caminho)
        dados = parser_dispatcher(texto_extraido)
        dados = validar_dados(dados)
        return templates.TemplateResponse("index.html", {"request": request, "dados": dados})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "erro": str(e)})
    finally:
        os.remove(caminho)
