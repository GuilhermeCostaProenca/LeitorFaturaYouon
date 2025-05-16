import os
from src.parser.enel.parser_enel_sp import parse_enel_sp

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def carregar_texto(nome_arquivo):
    caminho = os.path.join(BASE, "tests", "samples", nome_arquivo)
    with open(caminho, encoding="utf-8") as f:
        return f.read()

def test_residencial_enel_sp():
    texto = carregar_texto("enel_sp_residencial.txt")
    dados = parse_enel_sp(texto)

    assert dados["classe"] == "Residencial", f"Classe incorreta: {dados['classe']}"
    assert dados["media_consumo_fora_ponta_mwh"] > 0, "Consumo fora ponta deve ser maior que 0"

def test_comercial_enel_sp():
    texto = carregar_texto("enel_sp_comercial.txt")
    dados = parse_enel_sp(texto)

    assert dados["classe"] == "Comercial"
    assert dados["demanda_contratada_ponta_kw"] > 0
    assert dados["media_consumo_ponta_mwh"] > 0

def test_industrial_enel_sp():
    texto = carregar_texto("enel_sp_industrial.txt")
    dados = parse_enel_sp(texto)

    assert dados["classe"] == "Industrial"
    assert dados["media_consumo_ponta_mwh"] > 0
    assert dados["historico_demanda_fora_kw"] > 0
