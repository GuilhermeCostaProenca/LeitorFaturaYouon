import json
import requests

def carregar_token():
    with open("credentials/monday_token.json", "r") as f:
        cred = json.load(f)
    return cred["token"], cred["board_id"]

def enviar_para_monday(dados):
    token, board_id = carregar_token()
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    query = """
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
      create_item (
        board_id: $board_id,
        item_name: $item_name,
        column_values: $column_values
      ) {
        id
      }
    }
    """

    item_name = f"Fatura - {dados.get('media_consumo_hfp', 0):.2f} MWh HFP"
    column_values = json.dumps({
        "texto": f"Média FP: {dados['media_fp']}, Média P: {dados['media_p']}",
        "números": dados['ultrapassagem_fp'],
        "números6": dados['ultrapassagem_p']
    })

    payload = {
        "query": query,
        "variables": {
            "board_id": board_id,
            "item_name": item_name,
            "column_values": column_values
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("[MONDAY] Enviado com sucesso! ID:", response.json())
    else:
        print("[MONDAY] ERRO:", response.text)
