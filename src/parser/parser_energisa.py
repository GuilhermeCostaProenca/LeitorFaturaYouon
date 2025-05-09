from .base_parser import buscar, buscar_num, extrair_valores_historico

def parse(content: str):
    dados = {
        "distribuidora": "ENERGISA",
        "mercado_energia": "Livre" if "TUSD LIVRE" in content.upper() or "LIVRE" in content.upper() else "Cativo",
        "classe": buscar(r"Classe:?[\s]*([A-Za-z]+)", content),
        "subgrupo_tarifario": buscar(r"Subgrupo:?[\s]*([A-Za-z0-9]+)", content),
        "modalidade_tarifaria": buscar(r"Modalidade Tarifária:?[\s]*([A-Za-z ]+)", content),
        "tipo_energia": "I5",
        "subelemento": buscar(r"(?:Nº DA INSTALAÇÃO|MATRÍCULA|CÓDIGO UC)[\s:]*([\d]+)", content),
        "referencia": buscar(r"Referente a[\s:]*([A-Za-z]{3}/\d{4})", content),
        "vencimento": buscar(r"Vencimento[\s:]*([\d/]{8,10})", content),
        "valor_total": buscar(r"Valor a pagar \(R\$\)[\s:]*([\d.,]+)", content),
        "media_consumo_p": 0.0,
        "media_consumo_fp": 0.0,
        "hist_demanda_p": 0,
        "hist_demanda_fp": 0,
        "demanda_contratada_p": 0.0,
        "demanda_contratada_fp": 0.0,
        "ultrapassagem_p": 0,
        "ultrapassagem_fp": 0,
    }

    hp, hfp = extrair_valores_historico(content)
    if hp: dados["media_consumo_p"] = round(sum(hp[-12:])/len(hp[-12:]), 3)
    if hfp: dados["media_consumo_fp"] = round(sum(hfp[-12:])/len(hfp[-12:]), 3)

    dados["hist_demanda_p"] = max(hp[-12:]) if hp else 0
    dados["hist_demanda_fp"] = max(hfp[-12:]) if hfp else 0

    # Regex energisa: linha com Demanda TUSDG
    match_demanda = re.findall(r"Demanda.*?(\d{2,5})\s+.*?(\d{2,5})", content)
    if match_demanda:
        try:
            dados["demanda_contratada_fp"] = float(match_demanda[0][0])
            dados["demanda_contratada_p"] = float(match_demanda[0][1])
        except:
            pass

    dados["ultrapassagem_p"] = max(0, dados["hist_demanda_p"] - dados["demanda_contratada_p"])
    dados["ultrapassagem_fp"] = max(0, dados["hist_demanda_fp"] - dados["demanda_contratada_fp"])

    return dados
