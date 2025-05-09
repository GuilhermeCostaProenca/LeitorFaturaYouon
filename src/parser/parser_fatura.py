import re

def parse_fatura(content: str) -> dict:
    def buscar(padrao, default=""):
        match = re.search(padrao, content, re.IGNORECASE)
        return match.group(1).strip() if match else default

    def buscar_num(padrao):
        val = buscar(padrao)
        return float(val.replace('.', '').replace(',', '.')) if val else 0.0

    dados = {
        "name": "",  # Preenchido no Monday
        "subelemento": buscar(r"(?:Nº DA INSTALAÇÃO|MATRÍCULA|CÓDIGO UC)[\s:]*([\d]+)"),
        "distribuidora": buscar(r"\b(CEMIG|ENEL|CPFL|COPEL|ENERGISA|LIGHT|RGE|CEEE|EQUATORIAL)\b"),
        "mercado_energia": "Livre" if "TUSD LIVRE" in content.upper() or "LIVRE" in content.upper() else "Cativo",
        "classe": buscar(r"Classe\s+([A-Za-z]+)"),
        "subgrupo_tarifario": buscar(r"Subgrupo:?[\s]*([A-Za-z0-9]+)"),
        "modalidade_tarifaria": buscar(r"Modalidade Tarifária:?[\s]*([A-Za-z ]+)"),
        "tipo_energia": "Convencional" if "convencional" in content.lower() else "I5",
        "referencia": buscar(r"Referente a[\s:]*([A-Za-z]{3}/\d{4})"),
        "vencimento": buscar(r"Vencimento[\s:]*([\d/]{8,10})"),
        "valor_total": buscar(r"Valor a pagar \(R\$\)[\s:]*([\d.,]+)")
    }

    # 🔢 Histórico de consumo
    matches = re.findall(r"(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)/\d{2}[\s\n\r]+(\d+)[\s\n\r]+(\d+)", content)
    hp_values = []
    hfp_values = []

    for mes, hp, hfp in matches:
        try:
            hp_val = int(hp)
            hfp_val = int(hfp)
            hp_values.append(hp_val)
            hfp_values.append(hfp_val)
        except:
            continue

    dados["media_consumo_p"] = round(sum(hp_values[-12:]) / len(hp_values[-12:]), 3) if hp_values else 0.0
    dados["media_consumo_fp"] = round(sum(hfp_values[-12:]) / len(hfp_values[-12:]), 3) if hfp_values else 0.0
    dados["hist_demanda_p"] = max(hp_values[-12:]) if hp_values else 0
    dados["hist_demanda_fp"] = max(hfp_values[-12:]) if hfp_values else 0

    # ⚙️ Demandas contratadas
    dados["demanda_contratada_p"] = buscar_num(r"Demanda Ponta.*?(\d{2,5})")
    dados["demanda_contratada_fp"] = buscar_num(r"Demanda Fora Ponta.*?(\d{2,5})")

    # 📊 Ultrapassagem
    dados["ultrapassagem_p"] = max(0, dados["hist_demanda_p"] - dados["demanda_contratada_p"])
    dados["ultrapassagem_fp"] = max(0, dados["hist_demanda_fp"] - dados["demanda_contratada_fp"])

    return dados
