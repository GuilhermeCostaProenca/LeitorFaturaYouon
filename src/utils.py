import re

def to_float(texto: str) -> float:
    """
    Converte texto para float tratando erros comuns do OCR como vírgulas, pontos e caracteres estranhos.
    """
    if not texto:
        return 0.0
    try:
        # Remove caracteres que não são dígitos, vírgulas ou pontos
        texto = re.sub(r"[^\d,\.]", "", texto)

        # Corrige formatação com base no padrão mais comum
        if texto.count(",") == 1 and texto.count(".") >= 1:
            texto = texto.replace(".", "").replace(",", ".")
        elif texto.count(",") == 1 and texto.count(".") == 0:
            texto = texto.replace(",", ".")
        elif texto.count(".") > 1:
            texto = texto.replace(".", "")

        return float(texto)
    except:
        return 0.0
