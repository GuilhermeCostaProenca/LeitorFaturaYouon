import re

def to_float(texto: str) -> float:
    """
    Converte string para float de forma robusta, tratando OCR bugado e formatos diversos.
    Ex: '2.640', '2,640', '2.640,00', '2.640a', '2,640ª', etc.
    """
    if not texto:
        return 0.0
    try:
        # Remove qualquer caractere que não seja número, ponto ou vírgula
        texto = re.sub(r"[^\d,\.]", "", texto)

        # Se tiver mais vírgulas que pontos, assume vírgula como decimal
        if texto.count(",") == 1 and texto.count(".") >= 1:
            texto = texto.replace(".", "").replace(",", ".")
        elif texto.count(",") == 1 and texto.count(".") == 0:
            texto = texto.replace(",", ".")
        elif texto.count(".") > 1:
            texto = texto.replace(".", "")  # Remove milhares mal posicionados

        return float(texto)
    except:
        return 0.0

def extrair_valor_float(texto: str, padrao: str) -> float:
    """
    Aplica uma regex no texto e retorna o valor encontrado como float
    """
    match = re.search(padrao, texto, re.IGNORECASE)
    if match:
        return to_float(match.group(1))
    return 0.0

def gerar_alertas_default(dados: dict) -> list:
    alertas = []

    if dados.get("media_consumo_ponta_mwh", 0) == 0:
        alertas.append("Consumo ponta zerado ou não identificado.")

    if dados.get("media_consumo_fora_ponta_mwh", 0) == 0:
        alertas.append("Consumo fora ponta zerado ou não identificado.")

    if dados.get("demanda_contratada_ponta_kw", 0) == 0 and dados.get("demanda_contratada_fora_ponta_kw", 0) == 0:
        alertas.append("Demandas contratadas não encontradas.")

    if dados.get("historico_demanda_fora_ponta_kw", 0) == 0:
        alertas.append("Histórico de demanda fora ponta ausente.")

    return alertas
