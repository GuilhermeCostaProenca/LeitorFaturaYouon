from azure_reader import extrair_dados_pdf
from src.parser.parser_fatura import parse_fatura
from validador import salvar_preview, imprimir_preview
import sys

if __name__ == "__main__":
    path_pdf = sys.argv[1] if len(sys.argv) > 1 else "sample_faturas/exemplo.pdf"

    print(f"[INFO] Iniciando leitura de: {path_pdf}")
    resultado_azure = extrair_dados_pdf(path_pdf)
    content = resultado_azure.get("content", "")
    dados = parse_fatura(content)

    imprimir_preview(dados)
    salvar_preview(dados)
