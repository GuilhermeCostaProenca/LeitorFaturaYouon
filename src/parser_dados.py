def extrair_campos_engenharia(json_azure):
    linhas_texto = []
    if "content" in json_azure:
        linhas_texto = json_azure["content"].splitlines()
    else:
        for page in json_azure.get("pages", []):
            for line in page.get("lines", []):
                linhas_texto.append(line.get("content", ""))

    def buscar_linha(padrao):
        for linha in linhas_texto:
            if padrao.lower() in linha.lower():
                return linha
        return ""

    def extrair_valor_da_linha(linha):
        import re
        match = re.findall(r"\d+[\.,]?\d*", linha.replace(".", ","))
        return float(match[-1].replace(",", ".")) if match else 0

    dados = {
        "media_fp": extrair_valor_da_linha(buscar_linha("fora ponta")),
        "media_p": extrair_valor_da_linha(buscar_linha("ponta")),
        "demanda_contratada_fp": extrair_valor_da_linha(buscar_linha("demanda contratada fora")),
        "demanda_contratada_p": extrair_valor_da_linha(buscar_linha("demanda contratada ponta")),
        "hist_demanda_fp": extrair_valor_da_linha(buscar_linha("histórico demanda fora")),
        "hist_demanda_p": extrair_valor_da_linha(buscar_linha("histórico demanda ponta")),
    }

    dados["ultrapassagem_fp"] = max(0, dados["hist_demanda_fp"] - dados["demanda_contratada_fp"])
    dados["ultrapassagem_p"] = max(0, dados["hist_demanda_p"] - dados["demanda_contratada_p"])

    return dados