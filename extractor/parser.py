import re

def parse_basic_energy_info(text):
    result = {}

    if "Cliente Livre" in text or "Tarifa Livre" in text:
        result["mercado"] = "Livre"
    elif "Grupo B" in text or "Cativo" in text:
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

    tipo_match = re.search(r"tipo de energia\s*[:\-]?\s*(I\d|convencional)", text, re.IGNORECASE)
    result["tipo_energia"] = tipo_match.group(1).upper() if tipo_match else "Não identificado"

    consumo_ponta = re.search(r"ACL\s*-\s*Ponta.*?(\d{1,3}(?:\.\d{3})*,\d{2})", text)
    consumo_fp = re.search(r"ACL\s*-\s*Fora\s*de\s*Ponta.*?(\d{1,3}(?:\.\d{3})*,\d{2})", text)
    result["consumo_ponta_kWh"] = consumo_ponta.group(1).replace('.', '').replace(',', '.') if consumo_ponta else None
    result["consumo_fora_ponta_kWh"] = consumo_fp.group(1).replace('.', '').replace(',', '.') if consumo_fp else None

    demanda_ponta = re.search(r"Demanda Ponta.*?(\d{1,3}(?:,\d{1,2})?)", text)
    demanda_fp = re.search(r"Demanda Fora.*?(\d{1,3}(?:,\d{1,2})?)", text)
    result["demanda_contratada_ponta_kW"] = demanda_ponta.group(1).replace(',', '.') if demanda_ponta else None
    result["demanda_contratada_fora_kW"] = demanda_fp.group(1).replace(',', '.') if demanda_fp else None

    return result
