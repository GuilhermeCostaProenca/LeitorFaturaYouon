from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os

def load_azure_credentials():
    with open("credentials/azure_secrets.json", "r") as f:
        secrets = json.load(f)
    return secrets["endpoint"], secrets["key"]

def extrair_dados_pdf(path_pdf: str):
    endpoint, key = load_azure_credentials()
    
    client = DocumentAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    with open(path_pdf, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", document=f)
        result = poller.result()

    dados_extraidos = []
    for page in result.pages:
        pagina = []
        for table in page.tables:
            tabela = []
            for cell in table.cells:
                tabela.append({
                    "content": cell.content,
                    "row": cell.row_index,
                    "col": cell.column_index
                })
            pagina.append(tabela)
        dados_extraidos.append(pagina)

    # Salvar o JSON bruto opcionalmente (log)
    os.makedirs("saida", exist_ok=True)
    with open("saida/log_raw_azure.json", "w") as f:
        json.dump(result.to_dict(), f, indent=4)

    return result.to_dict()  # retorno total do Azure (para parser_dados)
