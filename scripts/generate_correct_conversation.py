import  random
import json
from tqdm import tqdm
import lmstudio as lms
from utils import *
import os

name_model = "gemma-3-27b-it"
model = lms.llm(name_model)

# liste per la selezione dei campi da valutare
trigger = [['trigger_channel'], ['trigger_channel', 'trigger_title'], ['trigger_channel', 'trigger_title', 'trigger_fields'], ['trigger_channel', 'trigger_title', 'trigger_fields', 'trigger_fields_values']]
action = [['action_channel'], ['action_channel', 'action_title'], ['action_channel', 'action_title', 'action_fields'], ['action_channel', 'action_title', 'action_fields', 'action_fields_values']]
triggerAndAction = [['trigger_channel', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel', 'action_title']]


with open("dataset/values_prova_completo.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)


for i, entry in enumerate(tqdm(dataset, total=len(dataset))):
    current_text = ""   # stringa di output contenente tutta la conversazione

    # scelta di iniziare o meno con i campi action
    isAction = random.choice([0, 1])
    if isAction:
        fields = random.choice(triggerAndAction)
    else:
        fields = random.choice(trigger)

    
    # fields è una lista con i campi selezionati fino a quel momento 
    # entry è la regola trigger-action presente nel dataset
    # bf_current è un dizionario (chiave = nome del campo, valore = valore del campo)
    # str_trigger_action_current è la formattazione in str dell'entry, solo per i campi contenuti in fields
    bf_current, str_trigger_action_current = get_prompt_input(fields, entry)
    
    prompt = get_prompt(isFirst = True, trigger_action_current = str_trigger_action_current, trigger_action_past = "")
    # Chiamata al modello
    current_text += str(model.respond(prompt))
    current_text += "\n" + str(bf_current) + "\n"

    str_trigger_action_past = str_trigger_action_current

    # Generazione solo delle trigger (prima trigger e poi action)
    # devono essere 4 stringhe con 't' -> cioè i 4 campi della trigger
    # while not (len(fields) >= 4 and sum(s.startswith('T') for s in fields) == 4):
    while not (sum(s.startswith('t') for s in fields) == 4):
        new_fields = random.choice(trigger)    
        
        if not set(new_fields).issubset(fields):
            new_elements = set(new_fields) - set(fields)
            new_elements = list(new_elements)
            fields += new_elements  # si tiene traccia dei campi correnti

            bf_new, str_trigger_action_current = get_prompt_input(new_elements, entry)
            
            bf_current = bf_current | bf_new   # bf_new è il dizionario di new_elements

            prompt = get_prompt(isFirst = False, trigger_action_current = str_trigger_action_current, trigger_action_past = str_trigger_action_past)
            # Chiamata al modello
            current_text += str(model.respond(prompt))
            current_text += "\n" + str(bf_current) + "\n"

            str_trigger_action_past= str_trigger_action_current

    # devono essere 4 stringhe con 'a' -> cioè i 4 campi dell'action
    while not (sum(s.startswith('a') for s in fields) == 4):
        new_fields = random.choice(action)    
        
        if not set(new_fields).issubset(fields):
            new_elements = set(new_fields) - set(fields)
            new_elements = list(new_elements)
            fields += new_elements

            bf_new, str_trigger_action_current = get_prompt_input(new_elements, entry)
            
            bf_current = bf_current | bf_new # bf_new è il dizionario di new_elements

            prompt = get_prompt(isFirst = False, trigger_action_current = str_trigger_action_current, trigger_action_past = str_trigger_action_past)
            # Chiamata al modello
            current_text += str(model.respond(prompt))
            current_text += "\n" + str(bf_current) + "\n"

            str_trigger_action_past= str_trigger_action_current
    
    """
        SALVATAGGIO SU FILE DEL RISULTATO
    """
    # Percorso del file
    file_path = f"output_conversazione_incrementale/{name_model}/output{i}.txt"

    # Crea la directory se non esiste
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Scrivi il file
    with open(file_path, "w") as file:
        file.write(str(current_text))
            

    