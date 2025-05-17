
from copy import copy
import  random
import json
from tqdm import tqdm
import lmstudio as lms
from utils_correct_conversation import *
from utils_incorrect_conversation import *
from generate_correct_conversation import validate_prompt
import os
import ast
import json
import re



def count_fields(field_str):
    if isinstance(field_str, str) and field_str.strip():
        return len([item.strip() for item in field_str.strip('"').split(',') if item.strip()])
    return 0


def update_bf_error(text: str, bf_current: dict) -> dict:
    """
    - text: la stringa contenente 'ERROR:' seguito da coppie chiave: 'valore'(,'valore2')...
    - bf_current: dizionario di partenza; ne vengono rimosse le chiavi trovate nel testo
    Restituisce bf_current modificato.
    """
    # 1) Estrai la parte dopo 'ERROR:'
    parts = text.split('ERROR:', 1)
    if len(parts) < 2:
        return bf_current
    error_part = parts[1]

    # 2) Trova tutte le coppie chiave: 'valore'(,'valore2')...
    pattern = r"(\w+):\s*('(?:[^']|\\')*'(?:\s*,\s*'(?:[^']|\\')*')*)"
    matches = re.findall(pattern, error_part)

    # 3) Per ogni coppia, ricostruisci il valore (singolo o multiplo)
    parsed = {}
    for key, val_block in matches:
        # Estrai tutte le stringhe tra apici
        values = re.findall(r"'((?:[^']|\\')*)'", val_block)
        if len(values) > 1:
            # Unisci in un’unica stringa con virgole e apici
            joined = ", ".join(f"'{v}'" for v in values)
            parsed[key] = joined
        else:
            parsed[key] = values[0]

    # 4) Rimuovi da bf_current tutte le chiavi che compaiono in parsed
    for k in parsed:
        bf_current.pop(k, None)

    return bf_current


def generate_question_and_answer(fields_trigger_action, entry, fields, current_text, bf_current, str_trigger_action_past, old_response, isAction = False, correct = True):
    """
        Metodo per generare question e answer tramite la selezione casuale dagli elementi nella lista 'fields_trigger_action'.
        fields_trigger_action -> campi della regola trigger-action
    """
    if isAction:
        str_descrizione = 'action'
    else:
        str_descrizione = 'trigger'

    empty_fields_list = ['trigger_fields', 'trigger_fields_values', 'action_fields', 'action_fields_values']

    # Generazione solo delle componenti trigger o action
    # devono essere 4 stringhe con 'trigger'/'action' -> cioè i 4 campi della trigger/action
    while not (sum(s.startswith(str_descrizione) for s in fields) == 4):
        new_fields = []
        # generazione casuale dell'elemento
        index = random.randint(0, len(fields_trigger_action) - 1)
        new_fields = fields_trigger_action[index]
        
        # controllo che i nuovi elementi non siano già presenti nella lista
        if not set(new_fields).issubset(fields):
            # estrazione degli elementi non ancora generati
            new_elements = set(new_fields) - set(fields)
            new_elements = list(new_elements)
            
            # update di fields per tenere traccia dei campi generati
            fields += new_elements  

            # bf_new è il dizionario di new_elements
            # str_trigger_action_current è la stringa per l'input del prompt
            bf_new, str_trigger_action_current = get_prompt_input(new_elements, entry)
            
            # merge tra i dizionari
            bf_current = bf_current | bf_new   

            if correct:
                # se la generazione deve essere corretta allora isError è fissato a  0
                isError = 0
            else:
                # genero il numero casuale per vedere se l'utterance deve avere o no l'errore
                isError = random.choice([0, 1])
            
            # La generazione con errori non viene effettuata per i campi fields e fields_values se questi sono vuoti
            if (set(new_elements).issubset(empty_fields_list)) and all(bf_new[element] == '' for element in new_elements):
                isError = 0

            if isError:
                # stringa del prompt incorretto
                prompt = get_incorrect_prompt(isFirst = False, trigger_action_current = str_trigger_action_current, 
                    trigger_action_past = str_trigger_action_past, old_response = old_response)
            else:       
                # stringa del prompt corretto 
                prompt = get_prompt(isFirst = False, trigger_action_current = str_trigger_action_current, 
                    trigger_action_past = str_trigger_action_past, old_response = old_response)
            
            # Chiamata al modello
            response = str(model.respond(prompt, config={"temperature": 0.6}))
            
            # current_text += response
            # current_text += "\nBelief State: " + str(bf_current) + "\n\n"

            # se ho l'errore allora devo correggere l'errore e poi 
            if isError:
                # aggiornamento del belief state rimuovendo gli errori generati
                bf_current = update_bf_error(response, bf_current)
                
                # salvataggio della risposta con errore
                current_text += response
                current_text += "\nBelief State: " + str(bf_current) + "\n\n"

                # current_text += "Clarification question\n"
                # stringa del prompt corretto 
                prompt = get_clarification_prompt(user_utterance=response, trigger_action_current=str_trigger_action_current)
            
                # Chiamata al modello
                response = str(model.respond(prompt, config={"temperature": 0.6}))

                # current_text += response
                # current_text += "\nBelief State: " + str(bf_current) + "\n\n"

                # Validazione della risposta - se l'utterance è corretta
                current_text, old_response = validate_prompt(response, str_trigger_action_current, current_text,
                                                isFirst = False, old_response = old_response, str_trigger_action_past = str_trigger_action_past,
                                                isClarification = True)
            else: 
                # Validazione della risposta - se l'utterance è corretta
                current_text, old_response = validate_prompt(response, str_trigger_action_current, current_text,
                                                isFirst = False, old_response = old_response, str_trigger_action_past = str_trigger_action_past)

            # current_text += response + "\n"
            current_text += "\nBelief State: " + str(bf_current) + "\n\n"
            # old_response = response

            str_trigger_action_past = str_trigger_action_current


    return fields, current_text, bf_current, str_trigger_action_past, old_response


def generate_conversation(entry, correct = False):
    """
        Entry del dataset contenente la regola trigger action
        entry è la regola trigger-action presente nel dataset
    """
    # liste per la selezione dei campi da valutare
    trigger = [['trigger_channel'], 
                ['trigger_title'], 
                ['trigger_channel', 'trigger_title'], 
                ['trigger_channel', 'trigger_title', 'trigger_fields', 'trigger_fields_values']]
    
    action = [['action_channel'], 
                ['action_title'], 
                ['action_channel', 'action_title'], 
                ['action_channel', 'action_title', 'action_fields', 'action_fields_values']]
    
    triggerAndAction = [['trigger_channel', 'action_channel'],
                        ['trigger_title', 'action_title'],
                        ['trigger_channel', 'action_title'],
                        ['trigger_title', 'action_channel'],
                        ['trigger_channel', 'trigger_title', 'action_channel'], 
                        ['trigger_channel', 'trigger_title', 'action_title'],
                        ['trigger_channel', 'action_channel', 'action_title'],
                        ['trigger_title', 'action_channel', 'action_title'],                     
                        ['trigger_channel', 'trigger_title', 'action_channel', 'action_title'],
                        ['trigger_channel', 'trigger_title', 'trigger_fields', 'trigger_fields_values', 'action_channel', 'action_title', 'action_fields', 'action_fields_values']]

    # stringa di output contenente tutta la conversazione
    current_text = ""  

    num_trigger_fields = count_fields(entry.get('trigger_fields'))
    num_action_fields = count_fields(entry.get('action_fields'))

    # scelta di iniziare o meno con i campi sia trigger che action
    isTriggerAction = random.choice([0, 1])

    # scegliere se completare prima i campi action o trigger
    actionStart = random.choice([0, 1])
    
    if isTriggerAction:
        if num_trigger_fields <= 1 and num_action_fields <= 1:
            # se ci sono meno di 2 campi possiamo generare tutta la regola trigger action 
            index = random.randint(0, len(triggerAndAction) - 1)
            new_fields = triggerAndAction[index]
        else:
            # se ci sono più di 1 campo trigger o action, generiamo la conversazione incrementale
            index = random.randint(0, len(triggerAndAction) - 2)
            new_fields = triggerAndAction[index]

    elif actionStart:
        # iniziamo la generazione solo con la parte action
        index = random.randint(0, len(action) - 1)
        new_fields = action[index]
    else:
        # iniziamo la generazione solo con la parte trigger
        index = random.randint(0, len(trigger) - 1)
        new_fields = trigger[index]

    fields = copy(new_fields)

    # fields è una lista con i campi selezionati fino a quel momento 
    # bf_current è un dizionario (chiave = nome del campo, valore = valore del campo)
    # str_trigger_action_current è la formattazione dell'entry da passare al prompt, solo per i campi contenuti in fields
    bf_current, str_trigger_action_current = get_prompt_input(fields, entry)

    # se la generazione è quella con errore, genero il numero casuale per vedere se l'utterance deve avere o no l'errore
    if correct:
        isError = 0
    else:
        isError = random.choice([0, 1])
    
    if isError:
        # stringa del prompt per la gestione dell'errore - prima utterance
        prompt = get_incorrect_prompt(isFirst = True, trigger_action_current = str_trigger_action_current, trigger_action_past = "")
    else:
        # stringa del prompt per la gestione della generazione corretta - prima utterance
        prompt = get_prompt(isFirst = True, trigger_action_current = str_trigger_action_current, trigger_action_past = "")

    # Chiamata al modello per generare la prima utterance
    response = str(model.respond(prompt, config={"temperature": 0.6}))

    # Validazione della risposta (in questo caso è la prima utterance)
    if isError:
        # aggiornamento del belief state rimuovendo gli errori generati
        bf_current = update_bf_error(response, bf_current)

        # salvataggio della risposta con errore
        current_text += response
        current_text += "\nBelief State: " + str(bf_current) + "\n\n"

        # se la risposta contiene l'errore, allora si deve generare la clarification question
        # stringa del prompt per la clarification question
        prompt = get_clarification_prompt(user_utterance=response, trigger_action_current=str_trigger_action_current)
    
        # Chiamata al modello per generare la clarification question
        response = str(model.respond(prompt, config={"temperature": 0.6}))

        # Validazione della generazione del modello, nel caso si riesegue get_clarification_prompt
        current_text, response = validate_prompt(response, str_trigger_action_current, current_text, isClarification = True)
    else: 
        # se la risposta non contiene l'errore, allora si deve effettare la validazione
        # validazione della generazione corretta
        current_text, response = validate_prompt(response, str_trigger_action_current, current_text)

    # salvataggio del belief state dopo la validazione della risposta
    current_text += "\nBelief State: " + str(bf_current) + "\n\n"
    
    if actionStart:
        # si generano prima le componenti action
        # action
        fields, current_text, bf_current, str_trigger_action_past, old_response = generate_question_and_answer(fields_trigger_action=action, entry=entry, fields=fields, 
                                                                                                                current_text=current_text, bf_current=bf_current, 
                                                                                                                str_trigger_action_past=str_trigger_action_current, 
                                                                                                                old_response=response, isAction=True, correct = correct)

        # trigger
        fields, current_text, bf_current, str_trigger_action_past, old_response = generate_question_and_answer(fields_trigger_action=trigger, entry=entry, fields=fields, 
                                                                                                                current_text=current_text, bf_current=bf_current, 
                                                                                                                str_trigger_action_past=str_trigger_action_past, 
                                                                                                                old_response=old_response, isAction=False, correct = correct)
    
    else: 
        # si generano prima le componenti trigger
        # trigger
        fields, current_text, bf_current, str_trigger_action_past, old_response = generate_question_and_answer(fields_trigger_action=trigger, entry=entry, fields=fields, 
                                                                                                                current_text=current_text, bf_current=bf_current, 
                                                                                                                str_trigger_action_past=str_trigger_action_current, 
                                                                                                                old_response=response, isAction=False, correct = correct)

        # action
        fields, current_text, bf_current, str_trigger_action_past, old_response = generate_question_and_answer(fields_trigger_action=action, entry=entry, fields=fields, 
                                                                                                                current_text=current_text, bf_current=bf_current, 
                                                                                                                str_trigger_action_past=str_trigger_action_past, 
                                                                                                                old_response=old_response, isAction=True, correct = correct)
    
    return current_text



def parse_conversation_to_json(text: str) -> str:
    """
    Estrae dai blocchi separati da una riga vuota le parti:
    - righe che iniziano con "- Ruolo: testo"
    - la riga "Belief State: {…}"
    e restituisce un JSON indentato.
    """
    # Splitting in blocchi separati da riga vuota
    blocks = re.split(r'\n\s*\n', text.strip())
    result = []

    for block in blocks:
        entry = {}
        # Estrai tutte le linee "- Ruolo: testo"
        for role, utterance in re.findall(r'^- (\w+): (.+)$', block, re.MULTILINE):
            entry[role] = utterance.strip()

        # Estrai il dizionario della Belief State e convertilo in dict Python
        match = re.search(r"Belief State:\s*(\{.*\})", block)
        if match:
            # ast.literal_eval per sicurezza, trasforma la stringa in dict
            belief_state = ast.literal_eval(match.group(1))
            entry['Belief State'] = belief_state

        # Aggiungi all’elenco solo se abbiamo trovato almeno un ruolo
        if entry:
            result.append(entry)

    # Serializza in JSON
    return json.dumps(result)



if __name__ == "__main__":

    name_model = "gemma-3-27b-it"
    model = lms.llm(name_model)


    with open("dataset/values_prova_completo.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for i, entry in enumerate(tqdm(dataset, total=len(dataset))):
        
        correct_conversation = generate_conversation(entry, correct = True)
        incorrect_conversation = generate_conversation(entry, correct = False)

        # Togliere tutti i vari commenti da current_text
        # Salvataggio del risultato

        conversation = "Conversazione corretta\n" + correct_conversation + "Conversazione NON corretta\n" + incorrect_conversation

        """
            SALVATAGGIO SU FILE DEL RISULTATO
        """
        # Percorso del file
        file_path = f"output_2conversazioni/{name_model}/output{i}.txt"

        # Crea la directory se non esiste
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Scrivi il file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(conversation))