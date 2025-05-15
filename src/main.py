import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.azure_reader import extrair_texto_azure
from src.parser_dispatcher import parser_dispatcher
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
        return templates.TemplateResponse("index.html", {
            "request": request,
            "erro": "Formato inválido. Envie um PDF."
        })

    caminho = f"temp/{fatura.filename}"
    os.makedirs("temp", exist_ok=True)

    try:
        # Salva o PDF
        with open(caminho, "wb") as buffer:
            buffer.write(await fatura.read())

        # 🔍 Extrai texto com Azure
        print("\n🔎 EXTRAINDO TEXTO DO OCR...")
        texto_extraido = extrair_texto_azure(caminho)
        print("\n📄 TEXTO OCR BRUTO:")
        print("=" * 60)
        print(texto_extraido[:3000])  # só os primeiros 3000 caracteres
        print("=" * 60)

        # 🔍 Dispara o parser
        print("\n🧠 INICIANDO PARSER...")
        dados = parser_dispatcher(texto_extraido)

        # ✅ Valida os dados
        dados = validar_dados(dados)

        print("\n📊 DADOS EXTRAÍDOS:")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

        return templates.TemplateResponse("index.html", {
            "request": request,
            "dados": dados,
            "texto_ocr": texto_extraido[:3000]  # pode exibir o texto se quiser no HTML
        })

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "erro": str(e)
        })

    finally:
        # Limpa o arquivo temporário
        os.remove(caminho)
