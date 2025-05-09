import re

def buscar(pattern, content, default=""):
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else default

def buscar_num(pattern, content, default=0.0):
    val = buscar(pattern, content)
    try:
        return float(val.replace('.', '').replace(',', '.'))
    except:
        return default

def extrair_valores_historico(content):
    hp, hfp = [], []
    matches = re.findall(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{2}[\s\n\r]+(\d+)[\s\n\r]+(\d+)", content)
    for _, p, fp in matches:
        try:
            hp.append(int(p))
            hfp.append(int(fp))
        except:
            continue
    return hp, hfp
