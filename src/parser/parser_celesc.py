import re
from typing import Dict


def parser_celesc(texto: str) -> Dict:
    """
    Parser robusto para faturas da CELESC (Santa Catarina).
    """

    def extrair(regex, tipo=str, padrao_padrao=None):
        match = re.search(regex, texto, re.IGNORECASE)
        if not match:
            return padrao_padrao
        try:
            return tipo(match.group(1).replace(".", "").replace(",", "."))
        except:
            return padrao_padrao

    # === Distribuidora
    distribuidora = "CELESC"

    # === Mercado
    mercado = "Livre" if "ambiente de contratação livre" in texto.lower() else "Cativo"

    # === Classe
    if "residencial" in texto.lower():
        classe = "Residencial"
    elif "industrial" in texto.lower():
        classe = "Industrial"
    elif "comercial" in texto.lower():
        classe = "Comercial"
    elif "rural" in texto.lower():
        classe = "Rural"
    else:
        classe = "Não identificado"

    # === Subgrupo tarifário e modalidade
    subgrupo = extrair(r"Subgrupo tarif.rio\s*:?\s*([AB]\d+[a-zA-Z]*)") or "A4"
    modalidade = "Verde" if "verde" in texto.lower() else ("Azul" if "azul" in texto.lower() else "Convencional")

    # === Tipo de energia
    tipo_energia = "i5" if re.search(r"tens.ão.*(13|15|23|34|69|88|138|230)[ .]?k?v", texto, re.IGNORECASE) else "convencional"

    # === Médias de consumo
    media_ponta = extrair(r"m.\s*consumo.*ponta.*?(\d+[.,]\d+).*?mwh", float, 0)
    media_fp = extrair(r"m.\s*consumo.*fora\s*ponta.*?(\d+[.,]\d+).*?mwh", float, 0)

    # === Demandas contratadas
    demanda_contratada_ponta = extrair(r"demanda contratada.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)
    demanda_contratada_fp = extrair(r"demanda contratada.*fora\s*ponta.*?(\d+[.,]\d+).*?kw", float, 0)

    # === Histórico demanda medida
    historico_ponta = extrair(r"demanda medida.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)
    historico_fp = extrair(r"demanda medida.*fora\s*ponta.*?(\d+[.,]\d+).*?kw", float, 0)

    # === Ultrapassagem (histórico - contratada)
    ultrapassagem_ponta = max(0, historico_ponta - demanda_contratada_ponta)
    ultrapassagem_fp = max(0, historico_fp - demanda_contratada_fp)

    return {
        "distribuidora": distribuidora,
        "mercado_energia": mercado,
        "classe": classe,
        "subgrupo_tarifario": subgrupo,
        "modalidade_tarifaria": modalidade,
        "tipo_energia": tipo_energia,
        "media_consumo_ponta_mwh": round(media_ponta, 3),
        "media_consumo_fora_ponta_mwh": round(media_fp, 3),
        "demanda_contratada_ponta_kw": round(demanda_contratada_ponta, 2),
        "demanda_contratada_fora_ponta_kw": round(demanda_contratada_fp, 2),
        "historico_demanda_ponta_kw": round(historico_ponta, 2),
        "historico_demanda_fora_ponta_kw": round(historico_fp, 2),
        "ultrapassagem_ponta_kw": round(ultrapassagem_ponta, 2),
        "ultrapassagem_fora_ponta_kw": round(ultrapassagem_fp, 2)
    }
