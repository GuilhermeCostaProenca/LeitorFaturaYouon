# import re
# from typing import Dict

# from .parser_enel import parse
# from .parser_neoenergia import parser_neoenergia
# from .parser_energisa import parse
# from .parser_equatorial import parser_equatorial
# from .parser_cpfl import parse
# from .parser_edp import parser_edp
# from .parser_cemig import parse
# from .parser_celesc import parser_celesc
# from .parser_light import parser_light
# from .parser_cooperativas import parser_cooperativas
# from .parser_copel import parser_copel


# def parser_fallback(texto: str) -> Dict:
#     """
#     Parser fallback genérico com heurísticas para qualquer layout desconhecido de fatura de energia.
#     """

#     def extrair(regex, tipo=str, padrao_padrao=None):
#         match = re.search(regex, texto, re.IGNORECASE)
#         if not match:
#             return padrao_padrao
#         try:
#             return tipo(match.group(1).replace(".", "").replace(",", "."))
#         except:
#             return padrao_padrao

#     # === Distribuidora
#     distribuidora = extrair(r"(enel|energisa|cemig|copel|celesc|edp|light|equatorial|cpfl|neoenergia|celetro|cooperativa)", str, "Desconhecida").upper()

#     # === Mercado
#     mercado = "Livre" if "ambiente de contratação livre" in texto.lower() else "Cativo"

#     # === Classe
#     if "residencial" in texto.lower():
#         classe = "Residencial"
#     elif "industrial" in texto.lower():
#         classe = "Industrial"
#     elif "comercial" in texto.lower():
#         classe = "Comercial"
#     elif "rural" in texto.lower():
#         classe = "Rural"
#     else:
#         classe = "Não identificado"

#     # === Subgrupo tarifário e modalidade
#     subgrupo = extrair(r"subgrupo.*?(a\d[a-z]?)", str, "A4")
#     modalidade = "Verde" if "modalidade.*verde" in texto.lower() else ("Azul" if "azul" in texto.lower() else "Convencional")

#     # === Tipo de energia
#     tipo_energia = "i5" if re.search(r"tens.ão.*(13|15|23|34|69|88|138|230).*kv", texto, re.IGNORECASE) else "convencional"

#     # === Médias de consumo
#     media_ponta = extrair(r"consumo.*ponta.*m[eé]dia.*?(\d+[.,]\d+).*?k?wh", float, 0)
#     media_fp = extrair(r"consumo.*fora.*ponta.*m[eé]dia.*?(\d+[.,]\d+).*?k?wh", float, 0)

#     # === Demandas contratadas
#     demanda_contratada_ponta = extrair(r"demanda contratada.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)
#     demanda_contratada_fp = extrair(r"demanda contratada.*fora.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)

#     # === Demandas medidas
#     historico_ponta = extrair(r"demanda medida.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)
#     historico_fp = extrair(r"demanda medida.*fora.*ponta.*?(\d+[.,]\d+).*?kw", float, 0)

#     ultrapassagem_ponta = max(0, historico_ponta - demanda_contratada_ponta)
#     ultrapassagem_fp = max(0, historico_fp - demanda_contratada_fp)

#     return {
#         "distribuidora": distribuidora,
#         "mercado_energia": mercado,
#         "classe": classe,
#         "subgrupo_tarifario": subgrupo,
#         "modalidade_tarifaria": modalidade,
#         "tipo_energia": tipo_energia,
#         "media_consumo_ponta_mwh": round(media_ponta, 3),
#         "media_consumo_fora_ponta_mwh": round(media_fp, 3),
#         "demanda_contratada_ponta_kw": round(demanda_contratada_ponta, 2),
#         "demanda_contratada_fora_ponta_kw": round(demanda_contratada_fp, 2),
#         "historico_demanda_ponta_kw": round(historico_ponta, 2),
#         "historico_demanda_fora_ponta_kw": round(historico_fp, 2),
#         "ultrapassagem_ponta_kw": round(ultrapassagem_ponta, 2),
#         "ultrapassagem_fora_ponta_kw": round(ultrapassagem_fp, 2)
#     }


# def parser_dispatcher(texto: str) -> Dict:
#     if "enel distribui" in texto.lower():
#         return parser_enel(texto)
#     elif "neoenergia" in texto.lower():
#         return parser_neoenergia(texto)
#     elif "energisa" in texto.lower():
#         return parser_energisa(texto)
#     elif "equatorial" in texto.lower():
#         return parser_equatorial(texto)
#     elif "cpfl" in texto.lower() or "rge" in texto.lower():
#         return parser_cpfl(texto)
#     elif "edp" in texto.lower():
#         return parser_edp(texto)
#     elif "cemig" in texto.lower():
#         return parser_cemig(texto)
#     elif "copel" in texto.lower():
#         return parser_copel(texto)
#     elif "celesc" in texto.lower():
#         return parser_celesc(texto)
#     elif "light" in texto.lower():
#         return parser_light(texto)
#     elif "cooperativa" in texto.lower() or "celetro" in texto.lower():
#         return parser_cooperativas(texto)
#     else:
#         return parser_fallback(texto)
