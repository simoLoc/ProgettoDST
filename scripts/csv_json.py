import csv
import json

def csv_to_json(csv_file, json_file):
    data = []
    
    with open(csv_file, mode='r', encoding='ISO-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            reordered_row = {
                "trigger_channel": row.get("trigger_channel", ""),
                "trigger_title": row.get("trigger_title", ""),
                "trigger_fields": row.get("trigger fields", ""),
                "action_channel": row.get("action_channel", ""),
                "action_title": row.get("action_title", ""),
                "action_fields": row.get("action fields", ""),
                "descrizione": row.get("descrizione", "")
            }
            data.append(reordered_row)
    
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"Conversione completata! JSON salvato in {json_file}")


csv_to_json('C:/Users/Utente/Desktop/DST/dataset_6k.csv', 'C:/Users/Utente/Desktop/DST/dataset_6k.json')