import os
from flask import Flask, render_template, request
from azure_reader import extrair_texto_azure
from src.parser.enel.parser_enel_sp import parse_enel_sp
from validador import validar_dados

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sample_faturas'))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files.get("fatura")
    if not arquivo:
        return render_template("index.html", erro="Nenhum arquivo enviado.")

    if not arquivo.filename.lower().endswith(".pdf"):
        return render_template("index.html", erro="Apenas arquivos PDF são aceitos.")

    caminho = os.path.join(UPLOAD_FOLDER, arquivo.filename)
    arquivo.save(caminho)

    try:
        texto = extrair_texto_azure(caminho)
        dados = parse_enel_sp(texto)
        dados = validar_dados(dados)
        return render_template("index.html", dados=dados)
    except Exception as e:
        return render_template("index.html", erro=str(e))

if __name__ == "__main__":
    app.run(debug=True)
