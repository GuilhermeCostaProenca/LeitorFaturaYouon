from .parser import parser_energisa, parser_cemig, parser_cpfl, parser_enel, parser_fallback

def identificar_grupo(content):
    content = content.upper()
    if "ENERGISA" in content:
        return "energisa"
    elif "CEMIG" in content:
        return "cemig"
    elif "ENEL" in content:
        return "enel"
    elif "CPFL" in content:
        return "cpfl"
    else:
        return "fallback"

def parser_dispatcher(content):
    grupo = identificar_grupo(content)
    if grupo == "energisa":
        return parser_energisa.parse(content)
    elif grupo == "cemig":
        return parser_cemig.parse(content)
    elif grupo == "cpfl":
        return parser_cpfl.parse(content)
    elif grupo == "enel":
        return parser_enel.parse(content)
    else:
        return parser_fallback.parse(content)
