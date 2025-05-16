def validar_dados(dados: dict) -> dict:
    """
    Valida os dados extraídos e adiciona alertas caso algum valor essencial esteja ausente ou zerado.
    """
    alertas = dados.get("alertas", [])

    if dados.get("media_consumo_ponta_mwh", 0) == 0:
        alertas.append("Consumo ponta zerado ou não identificado.")

    if dados.get("media_consumo_fora_ponta_mwh", 0) == 0:
        alertas.append("Consumo fora ponta zerado ou não identificado.")

    if dados.get("demanda_contratada_ponta_kw", 0) == 0 and dados.get("demanda_contratada_fora_kw", 0) == 0:
        alertas.append("Demandas contratadas não encontradas.")

    if dados.get("historico_demanda_fora_kw", 0) == 0:
        alertas.append("Histórico de demanda fora ponta ausente.")

    if dados.get("distribuidora", "") == "Desconhecida":
        alertas.append("Distribuidora não identificada corretamente.")

    dados["alertas"] = alertas
    return dados
