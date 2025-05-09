from . import parser_energisa, parser_cemig

def identificar_grupo(content):
    if "ENERGISA" in content:
        return "energisa"
    elif "CEMIG" in content:
        return "cemig"
    return "generico"

def parse_fatura(content):
    grupo = identificar_grupo(content)
    if grupo == "energisa":
        return parser_energisa.parse(content)
    elif grupo == "cemig":
        return parser_cemig.parse(content)
    else:
        raise ValueError("Distribuidora não identificada. Parser genérico não implementado ainda.")
