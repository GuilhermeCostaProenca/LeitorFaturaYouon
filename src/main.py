from azure_reader import extrair_dados_pdf
from parser_dados import extrair_campos_engenharia
from integrador_monday import enviar_para_monday

import sys

if __name__ == "__main__":
    path_pdf = sys.argv[1] if len(sys.argv) > 1 else "sample_faturas/fatura_exemplo.pdf"

    print("[INFO] Lendo fatura:", path_pdf)
    resultado_azure = extrair_dados_pdf(path_pdf)

    print("[INFO] Extraindo dados técnicos...")
    dados_processados = extrair_campos_engenharia(resultado_azure)

    print("[INFO] Enviando para o Monday...")
    enviar_para_monday(dados_processados)
    print("[SUCESSO] Processo concluído!")