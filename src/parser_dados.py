import re

def extrair_campos_tecnicos_from_text(content: str) -> dict:
    dados = {}

    # Instalação
    match = re.search(r"Nº DA INSTALAÇÃO\s*([\d]+)", content, re.IGNORECASE)
    if match:
        dados["instalacao"] = match.group(1)

    # Classe
    match = re.search(r"Classe\s+([A-Za-z]+)", content)
    if match:
        dados["classe"] = match.group(1)

    # Subclasse
    match = re.search(r"Subclasse\s+([A-Za-z]+)", content)
    if match:
        dados["subclasse"] = match.group(1)

    # Modalidade Tarifária
    match = re.search(r"Modalidade Tarifária\s+([A-Za-z ]+)", content)
    if match:
        dados["modalidade_tarifaria"] = match.group(1).strip()

    # Tipo de energia (ex: I5, convencional, etc)
    match = re.search(r"Componente Fio HP\s+kW\s+\d+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+[\d,.]+\s+([\d,.]+)", content)
    if match:
        dados["tipo_energia"] = "I5"

    # Média de consumo HFP (últimos 12 meses)
    match = re.findall(r"HFP\s+\d+\s+\d+\s+\d+\s+(\d+)", content)
    if match and len(match) >= 12:
        consumos = [int(x) for x in match[-12:]]
        dados["media_consumo_hfp"] = sum(consumos) / len(consumos)

    # Demanda contratada (ponta e fora ponta)
    match_fp = re.search(r"HFP\s+Demanda ativa\s+kW\s+[\d]+\s+[\d/:\s]+\s+(\d+)", content)
    match_p = re.search(r"HP\s+Demanda ativa\s+kW\s+[\d]+\s+[\d/:\s]+\s+(\d+)", content)
    if match_fp:
        dados["demanda_fp"] = int(match_fp.group(1))
    if match_p:
        dados["demanda_p"] = int(match_p.group(1))

    # Demanda registrada (últimos meses - histórico)
    match = re.findall(r"JAN/2[0-9]{2}\s+(\d+)\s+(\d+)", content)
    if match:
        demandas_fp = [int(fp) for _, fp in match]
        demandas_p = [int(p) for p, _ in match]
        dados["pico_demanda_fp"] = max(demandas_fp)
        dados["pico_demanda_p"] = max(demandas_p)

    return dados
