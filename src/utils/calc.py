def process_fatura_data(texto, distribuidora):
    # mock: substituir por lógica real por distribuidora
    if distribuidora == "cemig":
        return {
            "media_fp": 144.9,
            "media_p": 13.8,
            "demanda_contratada_fp": 600,
            "demanda_contratada_p": 600,
            "hist_demanda_fp": 462,
            "hist_demanda_p": 517,
            "ultrapassagem_fp": max(0, 462 - 600),
            "ultrapassagem_p": max(0, 517 - 600)
        }