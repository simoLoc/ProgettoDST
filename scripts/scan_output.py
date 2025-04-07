import re

def extract_fields_values(content):
    modified_content = re.sub(r'"trigger_fields_values"', 'trigger_fields_values', content, flags=re.IGNORECASE)
    modified_content = re.sub(r'"action_fields_values"', 'action_fields_values', modified_content, flags=re.IGNORECASE)
    trigger_content = modified_content.split("trigger_fields_values: ")[1]
    trigger_content = trigger_content.split("\n")[0]
    action_content = modified_content.split("action_fields_values: ")[1]
    action_content = action_content.split("\n")[0]

    return trigger_content, action_content



for i in range(5):
    # Apri il file in modalità lettura
    with open(f'output_values/gemma-3-12b-it/output{i}.txt', 'r', encoding='utf-8') as file:
        # Leggi tutto il contenuto del file
        content = file.read()
        trigger_content, action_content = extract_fields_values(content)

        print(f"File {i}")
        print(trigger_content)
        print(action_content)