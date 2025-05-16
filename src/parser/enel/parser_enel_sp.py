import re
from ...utils import to_float


def identificar_classe(texto):
    texto = texto.upper()
    if "INDUSTRIAL" in texto:
        return "Industrial"
    elif "COMÉRCIO" in texto or "COMERCIAL" in texto:
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

    historico = re.findall(r"(\d{2}/\d{4})\s+\d+(?:,\d+)?\s+\d+(?:,\d+)?\s+(\d+)[,.]?(\d*)", texto)
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

    extrair_subgrupo_modalidade(texto, dados)
    extrair_valor_por_campo("DEMANDA.*?CONTRATADA.*?(\d+[,.]?\d*)", texto, dados, "demanda_contratada_ponta_kw")
    dados["demanda_contratada_fora_kw"] = dados["demanda_contratada_ponta_kw"]

    extrair_consumo_generico("CONSUMO PONTA", texto, dados, "media_consumo_ponta_mwh")
    extrair_consumo_generico("CONSUMO FORA PONTA", texto, dados, "media_consumo_fora_ponta_mwh")

    extrair_historico_demanda(texto, dados)
    calcular_ultrapassagem(dados)
    return dados


def parse_industrial(texto: str, ano: int) -> dict:
    dados = estrutura_padrao("Industrial")

    extrair_subgrupo_modalidade(texto, dados)
    extrair_valor_por_campo("DEMANDA.*?CONTRATADA.*?(\d+[,.]?\d*)", texto, dados, "demanda_contratada_ponta_kw")
    dados["demanda_contratada_fora_kw"] = dados["demanda_contratada_ponta_kw"]

    extrair_consumo_generico("CONSUMO PONTA", texto, dados, "media_consumo_ponta_mwh")
    extrair_consumo_generico("CONSUMO FORA PONTA", texto, dados, "media_consumo_fora_ponta_mwh")

    extrair_historico_demanda(texto, dados)
    calcular_ultrapassagem(dados)
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


def extrair_valor_por_campo(padrao: str, texto: str, dados: dict, chave: str):
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        dados[chave] = to_float(match.group(1))
    else:
        dados["alertas"].append(f"{chave.replace('_', ' ').capitalize()} não identificado.")


def extrair_consumo_generico(rotulo: str, texto: str, dados: dict, chave: str):
    linhas = texto.splitlines()
    valores = []
    for linha in linhas:
        if rotulo.upper() in linha.upper():
            num = re.search(r"(\d+[.,]\d+)", linha)
            if num:
                valores.append(to_float(num.group(1)))
    if valores:
        dados[chave] = round(sum(valores[-12:]) / len(valores[-12:]) / 1000, 3)
    else:
        dados["alertas"].append(f"{rotulo} zerado ou não identificado.")


def extrair_subgrupo_modalidade(texto: str, dados: dict):
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


def extrair_historico_demanda(texto: str, dados: dict):
    linhas = texto.splitlines()
    ponta = []
    fora = []
    for linha in linhas:
        if re.search(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/", linha):
            numeros = re.findall(r"(\d+[.,]?\d*)", linha)
            if len(numeros) >= 3:
                ponta.append(to_float(numeros[1]))
                fora.append(to_float(numeros[2]))
    if ponta:
        dados["historico_demanda_ponta_kw"] = max(ponta[-12:])
    else:
        dados["alertas"].append("Histórico de demanda ponta ausente.")
    if fora:
        dados["historico_demanda_fora_kw"] = max(fora[-12:])
    else:
        dados["alertas"].append("Histórico de demanda fora ponta ausente.")


def calcular_ultrapassagem(dados: dict) -> None:
    dados["ultrapassagem_ponta_kw"] = max(0, dados["historico_demanda_ponta_kw"] - dados["demanda_contratada_ponta_kw"])
    dados["ultrapassagem_fora_kw"] = max(0, dados["historico_demanda_fora_kw"] - dados["demanda_contratada_fora_kw"])
