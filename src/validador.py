import json
from pathlib import Path

def salvar_preview(dados: dict, path="saida/extraido_preview.json"):
    Path("saida").mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def imprimir_preview(dados: dict):
    print("\n[VALORES EXTRAÍDOS PARA CONFERÊNCIA]")
    for k, v in dados.items():
        print(f"{k}: {v}")
