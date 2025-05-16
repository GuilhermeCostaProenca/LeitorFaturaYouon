import re
from ...utils import to_float

def identificar_classe(texto):
    texto = texto.upper()
    if re.search(r"\bINDU(STRIAL)?\b", texto):
        return "Industrial"
    elif re.search(r"\bCOM(\.|ÉRCIO|ERCIAL)?\b", texto):
        return "Comercial"
    elif "RESIDENCIAL" in texto:
        return "Residencial"
    elif "PODER PÚBLICO" in texto or "PODER PUBLICO" in texto:
        return "Poder público"
    else:
        return "Desconhecida"

def identificar_ano(texto):
    match = re.search(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/?(\d{2,4})", texto.upper())
    if match:
        ano = int(match.group(2))
        return 2000 + ano if ano < 100 else ano
    return None

def parse_enel_sp(texto: str) -> dict:
    classe = identificar_classe(texto)
    ano = identificar_ano(texto)

    if classe == "Residencial":
        return parse_residencial(texto, ano)
    elif classe == "Comercial":
        return parse_comercial(texto, ano)
    elif classe == "Industrial":
        return parse_industrial(texto, ano)
    else:
        return {"erro": "Classe não identificada ou parser não implementado."}

def parse_residencial(texto: str, ano: int) -> dict:
    dados = estrutura_padrao("Residencial")
    historico = re.findall(r"\n(\d{2}/\d{4})\s+\d+\s+\d+\s+(\d+)[,.]?(\d*)", texto)
    if historico:
        consumos = []
        for m in historico:
            valor = f"{m[1]}.{m[2]}" if m[2] else m[1]
            consumos.append(to_float(valor))
        if consumos:
            media = sum(consumos[-12:]) / len(consumos[-12:])
            dados["media_consumo_fora_ponta_mwh"] = round(media / 1000, 3)
    else:
        dados["alertas"].append("Histórico de consumo residencial não identificado.")
    return dados

def parse_comercial(texto: str, ano: int) -> dict:
    dados = estrutura_padrao("Comercial")
    dados.update(extrair_subgrupo_modalidade(texto, dados))
    extrair_demanda_contratada_por_maior_linha(texto, dados)
    extrair_consumo_por_medidor(texto, dados)
    extrair_historico_demanda(texto, dados)
    dados = calcular_ultrapassagem(dados)
    return dados

def parse_industrial(texto: str, ano: int) -> dict:
    dados = estrutura_padrao("Industrial")
    dados.update(extrair_subgrupo_modalidade(texto, dados))
    extrair_demanda_contratada_por_maior_linha(texto, dados)
    extrair_consumo_por_medidor(texto, dados)
    extrair_historico_demanda(texto, dados)
    dados = calcular_ultrapassagem(dados)
    return dados

def estrutura_padrao(classe: str) -> dict:
    return {
        "distribuidora": "Enel SP",
        "mercado_energia": "Cativo",
        "classe": classe,
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

def extrair_subgrupo_modalidade(texto: str, dados: dict) -> dict:
    match_sub = re.search(r"SUBGRUPO\s+(A[1-4]|AS|B[1-4])", texto.upper())
    if match_sub:
        dados["subgrupo_tarifario"] = match_sub.group(1)
    else:
        dados["alertas"].append("Subgrupo tarifário não identificado.")
    match_mod = re.search(r"MODALIDADE TARIF[ÁA]RIA\s+(VERDE|AZUL|CONVENCIONAL)", texto.upper())
    if match_mod:
        dados["modalidade_tarifaria"] = match_mod.group(1).capitalize()
    else:
        dados["alertas"].append("Modalidade tarifária não identificada.")
    return dados

def extrair_consumo_por_medidor(texto: str, dados: dict):
    consumos_ponta = re.findall(r'ENRG ATV PONTA[^\n\r]*?(\d+[.,]\d+)', texto)
    consumos_fora = re.findall(r'ENRG ATV F PONTA(?: INDU)?[^\n\r]*?(\d+[.,]\d+)', texto)

    if consumos_ponta:
        valores = [to_float(v) for v in consumos_ponta if to_float(v) > 0]
        if valores:
            dados["media_consumo_ponta_mwh"] = round(sum(valores[-12:]) / len(valores[-12:]) / 1000, 3)
        else:
            dados["alertas"].append("Consumo ponta zerado ou inválido.")
    else:
        dados["alertas"].append("Consumo ponta não identificado.")

    if consumos_fora:
        valores = [to_float(v) for v in consumos_fora if to_float(v) > 0]
        if valores:
            dados["media_consumo_fora_ponta_mwh"] = round(sum(valores[-12:]) / len(valores[-12:]) / 1000, 3)
        else:
            dados["alertas"].append("Consumo fora ponta zerado ou inválido.")
    else:
        dados["alertas"].append("Consumo fora ponta não identificado.")

def extrair_demanda_contratada_por_maior_linha(texto: str, dados: dict):
    matches = re.findall(r'DEMANDA(?:.*?)?(\d{1,4}[.,]?\d{0,3})', texto)
    valores = [to_float(m) for m in matches if to_float(m) > 0]
    if valores:
        maior = max(valores)
        dados["demanda_contratada_ponta_kw"] = maior
        dados["demanda_contratada_fora_kw"] = maior
    else:
        dados["alertas"].append("Demandas contratadas não encontradas.")

def extrair_historico_demanda(texto: str, dados: dict):
    historico = re.findall(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{2,4}\s+([\d.,]+)\s+([\d.,]+)", texto, re.DOTALL)
    if historico:
        ponta = [to_float(p) for (_, p, _) in historico[-12:]]
        fora = [to_float(f) for (_, _, f) in historico[-12:]]
        dados["historico_demanda_ponta_kw"] = max(ponta)
        dados["historico_demanda_fora_kw"] = max(fora)
    else:
        dados["alertas"].append("Histórico de demanda não identificado.")

def calcular_ultrapassagem(dados: dict) -> dict:
    dados["ultrapassagem_ponta_kw"] = max(0, dados["historico_demanda_ponta_kw"] - dados["demanda_contratada_ponta_kw"])
    dados["ultrapassagem_fora_kw"] = max(0, dados["historico_demanda_fora_kw"] - dados["demanda_contratada_fora_kw"])
    return dados
