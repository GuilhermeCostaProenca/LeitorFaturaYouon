from .base_parser import buscar, buscar_num, extrair_valores_historico

def parse(content: str):
    return {
        "distribuidora": buscar(r"(CEMIG|CPFL|ENEL|ENERGISA)", content),
        "subelemento": buscar(r"(?:Nº DA INSTALAÇÃO|MATRÍCULA|UNIDADE CONSUMIDORA)[\s:]*([\d]+)", content),
        "classe": buscar(r"Classe\s*([A-Za-z]+)", content),
        "subgrupo_tarifario": buscar(r"Subgrupo\s*([A-Za-z0-9]+)", content),
        "modalidade_tarifaria": buscar(r"Modalidade tarif[aá]ria\s*([A-Za-z\s]+)", content),
        "tipo_energia": "Convencional",
        "mercado_energia": "Livre" if "livre" in content.lower() else "Cativo",
        "referencia": buscar(r"Referente a\s*([\w/]+)", content),
        "vencimento": buscar(r"Vencimento\s*([\d/]+)", content),
        "valor_total": buscar(r"Total a pagar.*?([\d.,]+)", content),
        "media_consumo_p": 0.0,
        "media_consumo_fp": 0.0,
        "hist_demanda_p": 0,
        "hist_demanda_fp": 0,
        "demanda_contratada_p": 0.0,
        "demanda_contratada_fp": 0.0,
        "ultrapassagem_p": 0,
        "ultrapassagem_fp": 0
    }
