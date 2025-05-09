from flask import Flask, render_template, request
from azure_reader import ler_pdf_azure
from parser.parser_dispatcher import parse_fatura

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    arquivo = request.files["fatura"]
    caminho = f"sample_faturas/{arquivo.filename}"
    arquivo.save(caminho)

    print(f"[INFO] Arquivo recebido: {caminho}")
    texto = ler_pdf_azure(caminho)
    dados = parse_fatura(texto)

    return render_template("index.html", dados=dados)

if __name__ == "__main__":
    app.run(debug=True)
