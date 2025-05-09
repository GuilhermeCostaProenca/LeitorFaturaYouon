import os
import requests
from typing import Optional
from dotenv import load_dotenv
load_dotenv()


AZURE_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")


def extrair_texto_azure(caminho_arquivo: str) -> Optional[str]:
    """
    Extrai texto completo da fatura usando o Azure Form Recognizer v3.0.
    Retorna o texto consolidado.
    """
    if not AZURE_ENDPOINT or not AZURE_KEY:
        raise EnvironmentError("Azure Form Recognizer: variáveis de ambiente não configuradas.")

    with open(caminho_arquivo, "rb") as f:
        dados = f.read()

    url = f"{AZURE_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"

    headers = {
        "Content-Type": "application/pdf",
        "Ocp-Apim-Subscription-Key": AZURE_KEY
    }

    response = requests.post(url, headers=headers, data=dados)
    if response.status_code != 202:
        raise ValueError(f"Erro ao enviar para o Azure: {response.text}")

    operation_location = response.headers["operation-location"]

    # Esperar resposta final
    import time
    for _ in range(20):
        time.sleep(1.5)
        resultado = requests.get(operation_location, headers={"Ocp-Apim-Subscription-Key": AZURE_KEY}).json()
        if resultado.get("status") == "succeeded":
            break
    else:
        raise TimeoutError("Azure não finalizou a análise a tempo.")

    # Concatenar todo o conteúdo textual encontrado
    paginas = resultado.get("analyzeResult", {}).get("content", "")
    return paginas