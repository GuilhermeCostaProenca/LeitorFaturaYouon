# extractor/parser_energisa_mg.py

import re

def parse_energisa_ms(text):
    result = {"distribuidora_detectada": "ENERGISA MG"}
    lines = text.splitlines()

    for i in range(len(lines) - 2):
        atual = lines[i].strip().upper()
        prox = lines[i+1].strip().upper()
        valor = lines[i+2].strip().replace('.', '').replace(',', '.')

        if "PONTA" in atual and "ENERGIA ATIVA" in prox:
            if re.match(r'^\d+(\.\d{1,2})?$', valor):
                result["consumo_ponta_kWh"] = valor

        if "FORA PONTA" in atual and "ENERGIA ATIVA" in prox:
            if re.match(r'^\d+(\.\d{1,2})?$', valor):
                result["consumo_fora_ponta_kWh"] = valor

        if "DEMANDA PONTA" in atual:
            if re.match(r'^\d+(\.\d{1,2})?$', valor):
                result["demanda_contratada_ponta_kW"] = valor

        if "DEMANDA FORA PONTA" in atual:
            if re.match(r'^\d+(\.\d{1,2})?$', valor):
                result["demanda_contratada_fora_kW"] = valor

    result["mercado"] = "Cativo"
    result["classe"] = "Industrial"
    result["subgrupo_tarifario"] = "A4"
    result["modalidade_tarifaria"] = "Verde"
    result["tipo_energia"] = "Não identificado"

    campos_essenciais = [
        result.get("consumo_ponta_kWh"),
        result.get("consumo_fora_ponta_kWh"),
        result.get("demanda_contratada_ponta_kW"),
        result.get("demanda_contratada_fora_kW")
    ]
    result["precisa_revisao"] = any(v is None for v in campos_essenciais)

    return result