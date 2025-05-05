from copy import copy
import  random
import json
from tqdm import tqdm
import lmstudio as lms
from utils import *
import os


def generate_question_and_answer(fields_trigger_action, entry, fields, current_text, bf_current, str_trigger_action_past, old_response, isAction = False):
    """
        Metodo per generare question e answer tramite la selezione casuale dagli elementi nella lista 'fields_trigger_action'.
        fields_trigger_action -> campi della regola trigger-action
    """
    if isAction:
        str_descrizione = 'action'
    else:
        str_descrizione = 'trigger'

    # Generazione solo delle trigger (prima trigger e poi action)
    # devono essere 4 stringhe con 'trigger'/'action' -> cioè i 4 campi della trigger/action
    while not (sum(s.startswith(str_descrizione) for s in fields) == 4):
        new_fields = []
        # generazione casuale dell'elemento
        index = random.randint(0, len(fields_trigger_action) - 1)
        new_fields = fields_trigger_action[index]
        
        if not set(new_fields).issubset(fields):
            new_elements = set(new_fields) - set(fields)
            new_elements = list(new_elements)
            fields += new_elements  # si tiene traccia dei campi correnti

            bf_new, str_trigger_action_current = get_prompt_input(new_elements, entry)
            
            # merge tra i dizionari
            bf_current = bf_current | bf_new   # bf_new è il dizionario di new_elements

            # stringa del prompot
            prompt = get_prompt(isFirst = False, trigger_action_current = str_trigger_action_current, 
                trigger_action_past = str_trigger_action_past, old_response = old_response)
            
            # Chiamata al modello
            response = str(model.respond(prompt))
            current_text += response + "\n"
            current_text += str(bf_current) + "\n\n"
            old_response = response

            str_trigger_action_past = str_trigger_action_current

    
    return fields, current_text, bf_current, str_trigger_action_past



if __name__ == "__main__":

    name_model = "gemma-3-27b-it"
    model = lms.llm(name_model)

    # liste per la selezione dei campi da valutare
    trigger = [['trigger_channel'], ['trigger_channel', 'trigger_title'], ['trigger_channel', 'trigger_title', 'trigger_fields', 'trigger_fields_values']]
    action = [['action_channel'], ['action_channel', 'action_title'], ['action_channel', 'action_title', 'action_fields', 'action_fields_values']]
    triggerAndAction = [['trigger_channel', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel', 'action_title']]


    with open("dataset/values_prova_completo.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)


    for i, entry in enumerate(tqdm(dataset, total=len(dataset))):
        current_text = ""   # stringa di output contenente tutta la conversazione

        # scelta di iniziare o meno con i campi action
        isAction = random.choice([0, 1])
        
        if isAction:
            index = random.randint(0, len(triggerAndAction) - 1)
            new_fields = triggerAndAction[index]
        else:
            index = random.randint(0, len(trigger) - 1)
            new_fields = trigger[index]

        fields = copy(new_fields)
        # fields è una lista con i campi selezionati fino a quel momento 
        # entry è la regola trigger-action presente nel dataset
        # bf_current è un dizionario (chiave = nome del campo, valore = valore del campo)
        # str_trigger_action_current è la formattazione in str dell'entry, solo per i campi contenuti in fields
        bf_current, str_trigger_action_current = get_prompt_input(fields, entry)
        
        prompt = get_prompt(isFirst = True, trigger_action_current = str_trigger_action_current, trigger_action_past = "")

        # Chiamata al modello
        response = str(model.respond(prompt))
        current_text += response
        current_text += str(bf_current) + "\n\n"

        
        # trigger
        fields, current_text, bf_current, str_trigger_action_past = generate_question_and_answer(trigger, entry, fields, current_text, bf_current, 
                                                                                                str_trigger_action_current, response, isAction=False)

        # action
        fields, current_text, bf_current, str_trigger_action_past = generate_question_and_answer(action, entry, fields, current_text, bf_current, 
                                                                                                str_trigger_action_current, response, isAction=True)
        
        """
            SALVATAGGIO SU FILE DEL RISULTATO
        """
        # Percorso del file
        file_path = f"output_conversazione_incrementale/{name_model}/output{i}.txt"

        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Scrivi il file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(current_text))
                

