import re

# Mapeamento de possíveis padrões para cada campo
PADROES = {
    "consumo_ponta_kWh": [
        r"energia.*ponta.*?(\d{2,7}[.,]\d{2})",
        r"consumo.*ponta.*?(\d{2,7}[.,]\d{2})",
        r"kWh.*ponta.*?(\d{2,7}[.,]\d{2})"
    ],
    "consumo_fora_ponta_kWh": [
        r"energia.*fora.*ponta.*?(\d{2,7}[.,]\d{2})",
        r"consumo.*fp.*?(\d{2,7}[.,]\d{2})",
        r"kWh.*fp.*?(\d{2,7}[.,]\d{2})"
    ],
    "demanda_contratada_ponta_kW": [
        r"demanda.*ponta.*?(\d{2,5}[.,]?\d{0,2})",
        r"usd.*ponta.*?(\d{2,5}[.,]?\d{0,2})"
    ],
    "demanda_contratada_fora_kW": [
        r"demanda.*fora.*ponta.*?(\d{2,5}[.,]?\d{0,2})",
        r"usd.*fp.*?(\d{2,5}[.,]?\d{0,2})"
    ]
}

def aplicar_padrao(texto, padroes):
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1).replace('.', '').replace(',', '.')
    return None

def parse_basic_energy_info(text):
    result = {}

    # Mercado
    if "Cliente Livre" in text or "Tarifa Livre" in text:
        result["mercado"] = "Livre"
    elif "Grupo B" in text or "Cativo" in text:
        result["mercado"] = "Cativo"

    # Classe
    classe_match = re.search(r"Classificação:\s*(.*?)(?:\n|$)", text)
    result["classe"] = classe_match.group(1).strip() if classe_match else "Não identificado"

    # Subgrupo
    subgrupo_match = re.search(r"Classificação:.*?(A\d|B\d)", text)
    result["subgrupo_tarifario"] = subgrupo_match.group(1) if subgrupo_match else "Não identificado"

    # Modalidade
    if "Verde" in text:
        result["modalidade_tarifaria"] = "Verde"
    elif "Azul" in text:
        result["modalidade_tarifaria"] = "Azul"
    else:
        result["modalidade_tarifaria"] = "Não identificado"

    # Tipo de energia
    tipo_match = re.search(r"(I\d|convencional)", text, re.IGNORECASE)
    result["tipo_energia"] = tipo_match.group(1).upper() if tipo_match else "Não identificado"

    # Aplicar os padrões mapeados
    for campo, padroes in PADROES.items():
        result[campo] = aplicar_padrao(text, padroes)

    return result
