
import os
from flask import Flask, render_template, request
from azure_reader import extrair_dados_pdf
from parser.parser_dispatcher import parse_fatura

# Caminho correto para os templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

# Criação do app com caminho do template
app = Flask(__name__, template_folder=template_dir)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sample_faturas'))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files.get("fatura")
    if not arquivo:
        return render_template("index.html", erro="Nenhum arquivo foi enviado.")

    if not arquivo.filename.lower().endswith(".pdf"):
        return render_template("index.html", erro="Apenas arquivos PDF são aceitos.")

    caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
    arquivo.save(caminho)

    print(f"[INFO] Arquivo salvo: {caminho}")
    try:
        texto = extrair_dados_pdf(caminho)
        if isinstance(texto, dict):  # compatibilidade com dicionário retornado pela IA
            texto = texto.get("content", "")
        dados = parse_fatura(texto)
        return render_template("index.html", dados=dados)
    except Exception as e:
        print(f"[ERRO] {e}")
        return render_template("index.html", erro="Erro ao processar a fatura. Verifique o formato.")

if __name__ == "__main__":
    app.run(debug=True)
