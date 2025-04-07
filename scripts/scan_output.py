import re

def extract_fields_values(content):

    # rimozione " "
    modified_content = re.sub(r'"trigger_fields_values"', 'trigger_fields_values', content, flags=re.IGNORECASE)
    modified_content = re.sub(r'"action_fields_values"', 'action_fields_values', modified_content, flags=re.IGNORECASE)

    # rimozione testo precedente
    match_action = re.search(r'action_fields_values: [^\n]*', modified_content)
    match_trigger = re.search(r'trigger_fields_values: [^\n]*', modified_content)

    # rimozione ',' finale
    if match_action:
        extracted_text_action = match_action.group(0)
        if extracted_text_action.endswith(','):
            extracted_text_action = extracted_text_action[:-1]

    if match_trigger:
        extracted_text_trigger = match_trigger.group(0)
        if extracted_text_trigger.endswith(','):
            extracted_text_trigger = extracted_text_trigger[:-1]


    # rimozione [ ]
    match_text_action = re.search(r'\[([^\]]+)\]', extracted_text_action)
    if match_text_action:
        extracted_text_action = match_text_action.group(1)

    match_text_trigger = re.search(r'\[([^\]]+)\]', extracted_text_trigger)
    if match_text_trigger:
        extracted_text_trigger = match_text_trigger.group(1)


    return extracted_text_trigger, extracted_text_action



for i in range(5):
    # Apri il file in modalità lettura
    with open(f'output_values/gemma-3-12b-it/output{i}.txt', 'r', encoding='utf-8') as file:
        # Leggi tutto il contenuto del file
        content = file.read()
        text_trigger, text_action = extract_fields_values(content)
        print(f"File {i}")
        print(text_trigger)
        print(text_action)