import json
import pandas as pd

def export_to_json(data, output_path="saida.json"):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

def export_to_excel(data, output_path="saida.xlsx"):
    df = pd.DataFrame([data])
    df.to_excel(output_path, index=False)
