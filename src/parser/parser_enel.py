import re
from ..utils import to_float, extrair_valor_float, gerar_alertas_default


def parser_enel_sp(texto: str) -> dict:
    texto = texto.upper()

    dados = {
        "distribuidora": "Enel SP",
        "mercado_energia": "Livre" if "LIVRE" in texto else "Cativo",
        "classe": "Desconhecida",
        "subgrupo_tarifario": "Desconhecido",
        "modalidade_tarifaria": "Desconhecida",
        "tipo_energia": "Convencional",
        "media_consumo_ponta_mwh": 0.0,
        "media_consumo_fora_ponta_mwh": 0.0,
        "demanda_contratada_ponta_kw": 0.0,
        "demanda_contratada_fora_kw": 0.0,
        "historico_demanda_ponta_kw": 0.0,
        "historico_demanda_fora_kw": 0.0,
        "ultrapassagem_ponta_kw": 0.0,
        "ultrapassagem_fora_kw": 0.0,
        "alertas": []
    }

    # Classe
    match_classe = re.search(r"(RESIDENCIAL|COMERCIAL|INDUSTRIAL|RURAL|PODER P[ÚU]BLICO|ILUMINA[CÇ][ÃA]O)", texto)
    if match_classe:
        dados["classe"] = match_classe.group(1).capitalize()
    else:
        dados["alertas"].append("Classe não identificada.")

    # Subgrupo (prioriza A4)
    subgrupo_matches = re.findall(r"\b(A1|A2|A3|A3A|A4|AS|B1|B2|B3|B4)\b", texto)
    if "A4" in subgrupo_matches:
        dados["subgrupo_tarifario"] = "A4"
    elif subgrupo_matches:
        dados["subgrupo_tarifario"] = subgrupo_matches[0]
    else:
        dados["alertas"].append("Subgrupo tarifário não identificado.")

    # Modalidade tarifária
    match_modalidade = re.search(r"\b(VERDE|AZUL|CONVENCIONAL)\b", texto)
    if match_modalidade:
        dados["modalidade_tarifaria"] = match_modalidade.group(1).capitalize()
    else:
        dados["alertas"].append("Modalidade tarifária não identificada.")

    # Demanda contratada (quando disponível no formato claro)
    match_demanda_p = re.search(r"DEMANDA\s*-\s*KW\s*(\d+[.,]?\d*)", texto)
    match_demanda_fp = re.search(r"DEMANDA\s+FORA\s+PONTA\s*-\s*KW\s*(\d+[.,]?\d*)", texto)
    if match_demanda_p:
        dados["demanda_contratada_ponta_kw"] = to_float(match_demanda_p.group(1))
    else:
        dados["alertas"].append("Demanda contratada ponta não encontrada.")
    if match_demanda_fp:
        dados["demanda_contratada_fora_kw"] = to_float(match_demanda_fp.group(1))
    else:
        dados["alertas"].append("Demanda contratada fora ponta não encontrada.")

    # Consumo energético (kWh → MWh), baseado em leitura
    consumos_p = re.findall(r"ENRG\s+ATV\s+PONTA\s+\d+\s+\d+\s+\d+[.,]+\s+([\d.,]+)", texto)
    consumos_fp = re.findall(r"ENRG\s+ATV\s+F[\s\.]?PONTA(?:\s+(?:INDU|CAP))?\s+\d+\s+\d+\s+\d+[.,]+\s+([\d.,]+)", texto)

    if consumos_p:
        valores = [to_float(v) for v in consumos_p]
        dados["media_consumo_ponta_mwh"] = round(sum(valores[-12:]) / len(valores[-12:]) / 1000, 3)
    else:
        dados["alertas"].append("Consumo ponta zerado ou não identificado.")

    if consumos_fp:
        valores = [to_float(v) for v in consumos_fp]
        dados["media_consumo_fora_ponta_mwh"] = round(sum(valores[-12:]) / len(valores[-12:]) / 1000, 3)
    else:
        dados["alertas"].append("Consumo fora ponta zerado ou não identificado.")

    # Histórico de demanda (últimos 12 meses)
    historico = re.findall(r"\b\d{2}/\d{4}\s+(\d+[.,]?\d*)\s+(\d+[.,]?\d*)\s+\d+[.,]?\d*\s+\d+[.,]?\d*", texto)
    if historico:
        demandas_p = [to_float(x[0]) for x in historico]
        demandas_fp = [to_float(x[1]) for x in historico]
        if demandas_p:
            dados["historico_demanda_ponta_kw"] = max(demandas_p)
        if demandas_fp:
            dados["historico_demanda_fora_kw"] = max(demandas_fp)
    else:
        dados["alertas"].append("Histórico de demanda não identificado.")

    # Ultrapassagem (ponta e fora ponta)
    dados["ultrapassagem_ponta_kw"] = max(0, dados["historico_demanda_ponta_kw"] - dados["demanda_contratada_ponta_kw"])
    dados["ultrapassagem_fora_kw"] = max(0, dados["historico_demanda_fora_kw"] - dados["demanda_contratada_fora_kw"])

    return dados


def parser_enel_rj(texto: str) -> dict:
    dados = {
        "distribuidora": "Enel RJ" if "RJ" in texto.upper() else "Desconhecida",
        "mercado_energia": "Livre" if re.search(r"\bLIVRE\b", texto.upper()) else "Cativo",
        "classe": re.search(r"(RESIDENCIAL|COMERCIAL|INDUSTRIAL|RURAL|PODER PÚBLICO|ILUMINAÇÃO PÚBLICA)", texto.upper())
        .group(1).capitalize() if re.search(r"(RESIDENCIAL|COMERCIAL|INDUSTRIAL|RURAL|PODER PÚBLICO|ILUMINAÇÃO PÚBLICA)", texto.upper()) else "Desconhecida",
        "subgrupo_tarifario": re.search(r"\b(A1|A2|A3|A3a|A4|AS|B1|B2|B3|B4)\b", texto.upper())
        .group(1) if re.search(r"\b(A1|A2|A3|A3a|A4|AS|B1|B2|B3|B4)\b", texto.upper()) else "Desconhecido",
        "modalidade_tarifaria": re.search(r"\b(VERDE|AZUL|CONVENCIONAL)\b", texto.upper())
        .group(1).capitalize() if re.search(r"\b(VERDE|AZUL|CONVENCIONAL)\b", texto.upper()) else "Desconhecida",
        "tipo_energia": "convencional",
        "media_consumo_ponta_mwh": 0.0,
        "media_consumo_fora_ponta_mwh": 0.0,
        "demanda_contratada_ponta_kw": 0.0,
        "demanda_contratada_fora_kw": 0.0,
        "historico_demanda_ponta_kw": 0.0,
        "historico_demanda_fora_kw": 0.0,
        "ultrapassagem_ponta_kw": 0,
        "ultrapassagem_fora_kw": 0,
        "alertas": []
    }

    # Demanda contratada
    demanda_p = re.search(r"DEMANDA PONTA\s*-\s*KW\s*(\d+[.,]\d+)", texto, re.IGNORECASE)
    demanda_fp = re.search(r"DEMANDA FORA PONTA\s*-\s*KW\s*(\d+[.,]\d+)", texto, re.IGNORECASE)
    if demanda_p:
        dados["demanda_contratada_ponta_kw"] = to_float(demanda_p.group(1))
    else:
        dados["alertas"].append("Demanda contratada ponta não encontrada.")
    if demanda_fp:
        dados["demanda_contratada_fora_kw"] = to_float(demanda_fp.group(1))
    else:
        dados["alertas"].append("Demanda contratada fora ponta não encontrada.")

    # Histórico de demanda
    historico_p = re.findall(r"Demanda Faturada-KW\s+PONTA\s+[\d.,]+\s+([\d.,]+)", texto)
    historico_fp = re.findall(r"Demanda Faturada-KW\s+FORA PONTA\s+[\d.,]+\s+([\d.,]+)", texto)
    if historico_p:
        dados["historico_demanda_ponta_kw"] = max([to_float(h) for h in historico_p])
    else:
        dados["alertas"].append("Histórico de demanda ponta não identificado.")
    if historico_fp:
        dados["historico_demanda_fora_kw"] = max([to_float(h) for h in historico_fp])
    else:
        dados["alertas"].append("Histórico de demanda fora ponta não identificado.")

    # Média de consumo ponta e fora ponta (vários meses)
    consumos_p = re.findall(r"Energia Ativa-kWh\s+PONTA\s+[\d.,]+\s+[\d.,]+\s+[\d.,]+\s+([\d.,]+)", texto)
    consumos_fp = re.findall(r"Energia Ativa-kWh\s+FORA PONTA\s+[\d.,]+\s+[\d.,]+\s+[\d.,]+\s+([\d.,]+)", texto)
    if consumos_p:
        valores = [to_float(c) for c in consumos_p[:7]]
        dados["media_consumo_ponta_mwh"] = round(sum(valores) / len(valores) / 1000, 3)
    else:
        dados["alertas"].append("Média de consumo ponta não identificada.")
    if consumos_fp:
        valores = [to_float(c) for c in consumos_fp[:7]]
        dados["media_consumo_fora_ponta_mwh"] = round(sum(valores) / len(valores) / 1000, 3)
    else:
        dados["alertas"].append("Média de consumo fora ponta não identificada.")

    # Ultrapassagem
    dados["ultrapassagem_ponta_kw"] = max(0, dados["historico_demanda_ponta_kw"] - dados["demanda_contratada_ponta_kw"])
    dados["ultrapassagem_fora_kw"] = max(0, dados["historico_demanda_fora_kw"] - dados["demanda_contratada_fora_kw"])

    return dados


def parser_enel_ce(texto: str) -> dict:
    dados = {
        "distribuidora": "Enel CE",
        "mercado_energia": "Cativo",
        "classe": "Residencial" if "residencial" in texto.lower() else "Desconhecida",
        "subgrupo_tarifario": "B1" if "subgrupo" in texto.lower() else "Desconhecido",
        "modalidade_tarifaria": "Convencional",
        "tipo_energia": "convencional",
        "media_consumo_ponta_mwh": 0.0,
        "media_consumo_fora_ponta_mwh": 0.0,
        "demanda_contratada_ponta_kw": 0.0,
        "demanda_contratada_fora_kw": 0.0,
        "historico_demanda_ponta_kw": 0.0,
        "historico_demanda_fora_kw": 0.0,
        "ultrapassagem_ponta_kw": 0,
        "ultrapassagem_fora_kw": 0,
        "alertas": []
    }

    match = re.findall(r"\n(\d{2}/\d{4})\s+\d+\s+\d+\s+(\d+)[,.]?(\d*)", texto)
    if match:
        consumos = []
        for m in match:
            valor = f"{m[1]}.{m[2]}" if m[2] else m[1]
            consumos.append(float(valor))
        if consumos:
            media = sum(consumos[-12:]) / len(consumos[-12:])
            dados["media_consumo_fora_ponta_mwh"] = round(media / 1000, 3)
    else:
        dados["alertas"].append("Histórico de consumo não identificado.")

    return dados

def identificar_distribuidora(texto):
    if "Eletropaulo Metropolitana" in texto or "61.695.227/0001-93" in texto:
        return "enel_sp"
    elif "Ampla Energia" in texto or "33.050.071/0001-58" in texto:
        return "enel_rj"
    elif "Enel Distribuição Goiás" in texto or "01.042.362/0001-80" in texto:
        return "enel_go"
    elif "Enel Distribuição Ceará" in texto or "07.047.251/0001-70" in texto:
        return "enel_ce"
    return "desconhecida"

def parse(texto: str) -> dict:
    distribuidora = identificar_distribuidora(texto)

    if distribuidora == "enel_sp":
        return parser_enel_sp(texto)
    elif distribuidora == "enel_rj":
        return parser_enel_rj(texto)
    elif distribuidora == "enel_go":
        return parser_enel_go(texto)
    elif distribuidora == "enel_ce":
        return parser_enel_ce(texto)
    else:
        raise ValueError("Distribuidora Enel não identificada no texto da fatura.")
