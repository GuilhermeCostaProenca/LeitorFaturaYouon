from flask import Flask, render_template
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
from azure_reader import extrair_dados_pdf
from parser.parser_dispatcher import parse_fatura
import os

app = Flask(__name__)
UPLOAD_FOLDER = "sample_faturas"

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
        dados = parse_fatura(texto)
        return render_template("index.html", dados=dados)
    except Exception as e:
        print(f"[ERRO] {e}")
        return render_template("index.html", erro="Erro ao processar a fatura. Verifique o formato.")

if __name__ == "__main__":
    app.run(debug=True)
