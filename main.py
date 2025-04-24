from extractor.parser import parse_basic_energy_info
import fitz
import json
import sys
import os

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py
