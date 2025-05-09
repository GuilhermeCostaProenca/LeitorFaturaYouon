from .base_parser import buscar, buscar_num, extrair_valores_historico
import re

def parse(content: str):
    dados = {
        "distribuidora": "CPFL",
        "mercado_energia": "Livre" if "mercado livre" in content.lower() else "Cativo",
        "classe": buscar(r"Classe\s*([A-Za-z]+)", content),
        "subgrupo_tarifario": buscar(r"Subgrupo\s*([A-Za-z0-9]+)", content),
        "modalidade_tarifaria": buscar(r"Modalidade tarif[aá]ria\s*([A-Za-z\s]+)", content),
        "tipo_energia": "I5",  # heurística
        "subelemento": buscar(r"(?:Nº DA INSTALAÇÃO|Instalação|Unidade Consumidora)[\s:]*([\d]+)", content),
        "referencia": buscar(r"Referente a\s*([\w/]+)", content),
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

    match = re.findall(r"Demanda contratada.*?([\d.]+)\s+kW\s+([\d.]+)\s+kW", content)
    if match:
        dados["demanda_contratada_fp"] = float(match[0][0])
        dados["demanda_contratada_p"] = float(match[0][1])

    dados["ultrapassagem_p"] = max(0, dados["hist_demanda_p"] - dados["demanda_contratada_p"])
    dados["ultrapassagem_fp"] = max(0, dados["hist_demanda_fp"] - dados["demanda_contratada_fp"])

    return dados
