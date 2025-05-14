# extractor/parser_enel.py

import re

def parse_enel(text):
    result = {}

    # Mercado de Energia
    if "Cliente Livre" in text or "ACL" in text:
        result["mercado"] = "Livre"
    else:
        result["mercado"] = "Cativo"

    # Classe e Subgrupo Tarifário
    classe_match = re.search(r"Classificação:\s*(.*?)(?:\n|$)", text)
    result["classe"] = classe_match.group(1).strip() if classe_match else "Não identificado"

    subgrupo_match = re.search(r"Classificação:.*?(A\d|B\d)", text)
    result["subgrupo_tarifario"] = subgrupo_match.group(1) if subgrupo_match else "Não identificado"

    # Modalidade Tarifária
    if "Verde" in text:
        result["modalidade_tarifaria"] = "Verde"
    elif "Azul" in text:
        result["modalidade_tarifaria"] = "Azul"
    else:
        result["modalidade_tarifaria"] = "Não identificado"

    # Tipo de Energia
    tipo_match = re.search(r"Tipo de Energia\s*:?\s*(I\d|convencional)", text, re.IGNORECASE)
    result["tipo_energia"] = tipo_match.group(1).upper() if tipo_match else "Não identificado"

    # Consumo Ponta
    consumo_ponta = re.search(r"(?i)(consumo.*ponta|energia.*ponta).*?(\d{2,7}[.,]\d{2})", text)
    result["consumo_ponta_kWh"] = consumo_ponta.group(2).replace('.', '').replace(',', '.') if consumo_ponta else None

    # Consumo Fora Ponta
    consumo_fora_ponta = re.search(r"(?i)(consumo.*fora|energia.*fp).*?(\d{2,7}[.,]\d{2})", text)
    result["consumo_fora_ponta_kWh"] = consumo_fora_ponta.group(2).replace('.', '').replace(',', '.') if consumo_fora_ponta else None

    # Demanda Contratada Ponta
    demanda_ponta = re.search(r"(?i)(demanda.*ponta|usd.*ponta).*?(\d{2,5}[.,]?\d{0,2})", text)
    result["demanda_contratada_ponta_kW"] = demanda_ponta.group(2).replace(',', '.') if demanda_ponta else None

    # Demanda Contratada Fora Ponta
    demanda_fora_ponta = re.search(r"(?i)(demanda.*fora|usd.*fora).*?(\d{2,5}[.,]?\d{0,2})", text)
    result["demanda_contratada_fora_kW"] = demanda_fora_ponta.group(2).replace(',', '.') if demanda_fora_ponta else None

    return result