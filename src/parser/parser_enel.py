from .base_parser import buscar, buscar_num, extrair_valores_historico

def parse(content: str):
    dados = {
        "distribuidora": "Enel",
        "mercado_energia": "Livre" if "mercado livre" in content.lower() else "Cativo",
        "classe": buscar(r"Classe:\s*(\w+)", content),
        "subgrupo_tarifario": buscar(r"Subgrupo tarif[aá]rio:\s*([A-Za-z0-9]+)", content),
        "modalidade_tarifaria": buscar(r"Modalidade tarif[aá]ria:\s*([\w\s]+)", content),
        "tipo_energia": "I5",  # heurística por enquanto
        "subelemento": buscar(r"(?:Nº DA INSTALAÇÃO|Instalação)[\s:]*([\d]+)", content),
        "referencia": buscar(r"MÊS/ANO\s*([\w/]+)", content),
        "vencimento": buscar(r"Vencimento\s*([\d/]{8,10})", content),
        "valor_total": buscar(r"Total a pagar[\sR$]*([\d.,]+)", content),
        "media_consumo_p": 0.0,
        "media_consumo_fp": 0.0,
        "hist_demanda_p": 0,
        "hist_demanda_fp": 0,
        "demanda_contratada_p": 0.0,
        "demanda_contratada_fp": 0.0,
        "ultrapassagem_p": 0,
        "ultrapassagem_fp": 0
    }

    hp, hfp = extrair_valores_historico(content)
    if hp: dados["media_consumo_p"] = round(sum(hp[-12:]) / len(hp[-12:]), 3)
    if hfp: dados["media_consumo_fp"] = round(sum(hfp[-12:]) / len(hfp[-12:]), 3)

    dados["hist_demanda_p"] = max(hp[-12:]) if hp else 0
    dados["hist_demanda_fp"] = max(hfp[-12:]) if hfp else 0

    return dados
