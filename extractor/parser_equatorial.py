# extractor/parser_equatorial.py

import re

def parse_equatorial(text):
    result = {
        "distribuidora_detectada": "EQUATORIAL GO"
    }

    if "Cliente Livre" in text or "ACL" in text:
        result["mercado"] = "Livre"
    else:
        result["mercado"] = "Cativo"

    classe_match = re.search(r"Classificação:\s*(.*?)(?:\n|$)", text)
    result["classe"] = classe_match.group(1).strip() if classe_match else "Não identificado"

    subgrupo_match = re.search(r"Classificação:.*?(A\d|B\d)", text)
    result["subgrupo_tarifario"] = subgrupo_match.group(1) if subgrupo_match else "Não identificado"

    if "Verde" in text:
        result["modalidade_tarifaria"] = "Verde"
    elif "Azul" in text:
        result["modalidade_tarifaria"] = "Azul"
    else:
        result["modalidade_tarifaria"] = "Não identificado"

    tipo_match = re.search(r"Tipo de Energia\s*:?\s*(I\d|convencional)", text, re.IGNORECASE)
    result["tipo_energia"] = tipo_match.group(1).upper() if tipo_match else "Não identificado"

    consumo_ponta = re.search(r"(?i)(energia.*ponta|consumo.*ponta).*?(\d{2,7}[.,]\d{2})", text)
    result["consumo_ponta_kWh"] = consumo_ponta.group(2).replace('.', '').replace(',', '.') if consumo_ponta else None

    consumo_fp = re.search(r"(?i)(energia.*fora.*ponta|consumo.*fp).*?(\d{2,7}[.,]\d{2})", text)
    result["consumo_fora_ponta_kWh"] = consumo_fp.group(2).replace('.', '').replace(',', '.') if consumo_fp else None

    demanda_ponta = re.search(r"(?i)(demanda.*ponta|usd.*ponta).*?(\d{2,5}[.,]?\d{0,2})", text)
    result["demanda_contratada_ponta_kW"] = demanda_ponta.group(2).replace(',', '.') if demanda_ponta else None

    demanda_fp = re.search(r"(?i)(demanda.*fora.*ponta|usd.*fp).*?(\d{2,5}[.,]?\d{0,2})", text)
    result["demanda_contratada_fora_kW"] = demanda_fp.group(2).replace(',', '.') if demanda_fp else None

    campos_essenciais = [
        result.get("consumo_ponta_kWh"),
        result.get("consumo_fora_ponta_kWh"),
        result.get("demanda_contratada_ponta_kW"),
        result.get("demanda_contratada_fora_kW")
    ]
    result["precisa_revisao"] = any(valor is None for valor in campos_essenciais)

    return result
