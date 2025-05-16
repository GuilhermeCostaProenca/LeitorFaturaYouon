import os
import requests
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")


def extrair_texto_azure(caminho_arquivo: str) -> Optional[str]:
    """
    Extrai texto de um PDF usando o Azure Form Recognizer (v3.0).
    """
    if not AZURE_ENDPOINT or not AZURE_KEY:
        raise EnvironmentError("Azure: variáveis de ambiente não configuradas.")

    with open(caminho_arquivo, "rb") as f:
        conteudo = f.read()

    url = f"{AZURE_ENDPOINT}/formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"
    headers = {
        "Content-Type": "application/pdf",
        "Ocp-Apim-Subscription-Key": AZURE_KEY
    }

    resp = requests.post(url, headers=headers, data=conteudo)
    if resp.status_code != 202:
        raise ValueError(f"Erro Azure: {resp.text}")

    operation_location = resp.headers["operation-location"]

    for _ in range(20):
        time.sleep(1.5)
        result = requests.get(operation_location, headers={"Ocp-Apim-Subscription-Key": AZURE_KEY}).json()
        if result.get("status") == "succeeded":
            break
    else:
        raise TimeoutError("Azure não finalizou a análise a tempo.")

    return result.get("analyzeResult", {}).get("content", "")
