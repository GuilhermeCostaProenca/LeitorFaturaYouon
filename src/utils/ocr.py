import fitz  # PyMuPDF
import re

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    # Detectar distribuidora
    distribuidora = "desconhecida"
    if "CEMIG" in text.upper():
        distribuidora = "cemig"
    elif "CPFL" in text.upper():
        distribuidora = "cpfl"
    elif "ENEL" in text.upper():
        distribuidora = "enel"

    return text, distribuidora
