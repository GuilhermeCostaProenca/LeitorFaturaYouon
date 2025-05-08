from utils.ocr import extract_text_from_pdf
from utils.calc import process_fatura_data
from utils.export import export_to_json, export_to_excel

import sys

if __name__ == "__main__":
    path_pdf = sys.argv[1] if len(sys.argv) > 1 else "sample_faturas/fatura_exemplo.pdf"

    print("[INFO] Lendo fatura:", path_pdf)
    raw_text, distribuidora = extract_text_from_pdf(path_pdf)

    print("[INFO] Distribuidora detectada:", distribuidora)
    dados_processados = process_fatura_data(raw_text, distribuidora)

    export_to_json(dados_processados, output_path="saida/dados.json")
    export_to_excel(dados_processados, output_path="saida/dados.xlsx")
    print("[SUCESSO] Dados exportados com sucesso!")