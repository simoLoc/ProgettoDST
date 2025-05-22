from copy import copy
import  random
import json
from tqdm import tqdm
import lmstudio as lms
from utils_correct_conversation import *
from utils_incorrect_conversation import *
import os
import re

name_model = "gemma-3-27b-it"
model = lms.llm(name_model)

def get_system_user_utterances(user = True, response = ""):
    """
        Metodo per estrarre system o user utterance dalla risposta del modello.
    """
    if user:
        match = re.search(r'- User: (.*)', response, re.DOTALL)
        utterance = match.group(1).strip() if match else ''
    else:
        match = re.search(r'- System: (.*?)\n- User:', response, re.DOTALL)
        utterance = match.group(1).strip() if match else ''

    # print(f"Utterance (user =) {user}: {utterance}")

    return utterance


def validate_prompt(response, str_trigger_action_current, current_text, isFirst = True, old_response = "", str_trigger_action_past = "",  isClarification = False):
    """
        Metodo per validare se la user response generata contiene tutti i campi richiesti.        
        - response: utterance sulla quale fare validazione
        - str_trigger_action_current: stringa dei campi trigger action correnti
        - current_text: testo corrente della conversazione
        - isFirst: flag per indicare se si tratta della prima utterance
        - old_response: risposta precedente del modello
        - str_trigger_action_past: stringa dei campi trigger action passati
        - isClarification: flag per indicare se si deve generare la clarification question
    """
    # Estrazione della user utterance
    user_utterance = get_system_user_utterances(response = response)

    # current_text += "User utterance 0:" + user_utterance + "\n"

    i = 0 
    validation_result = False

    # Validazione della user utterance
    while i <= 2:
        validation_prompt = get_validation_prompt(user_utterance = user_utterance, trigger_action_current = str_trigger_action_current)
        validation_response = str(model.respond(validation_prompt, config={"temperature": 0.8}))

        validation_response = validation_response.strip()

        # current_text += "BF - state:" + str_trigger_action_current + "\n"
        # current_text += "Risposta alla validazione: " + validation_response + "\n"

        # effettuo lo split della risposta valutando il risultato dopo il potenziale l'esempio (fornito nel prompt)
        parts = validation_response.split("### EXAMPLE 1 TRIGGER-ACTION RULES\n## INPUT\n## UTTERANCE\n\nUser: I want you to monitor all new Facebook posts that have a photo and a specific hashtag.\n## FIELDS OF THE TRIGGER-ACTION RULE FOR UTTERANCE\ntrigger_channel: 'Facebook'\ntrigger_title: 'New photo post by you with hashtag'\n\n## OUTPUT\nResult: 1")

        # Se la validazione è corretta allora "1" sarà contenuto nell'ultimo elemento di parts
        if "1" in parts[len(parts)-1]:
            # print(f"Validazione {i} ok")
            # current_text += f"Validazione {i} ok"
            validation_result = True
            break
        else:
            # print(f"Validazione {i} no")
            # current_text += f"Validazione {i} no"
            i += 1
            
            # se la validazione non è corretta devo rieseguire la generazione (del clarification prompt o del prompt corretto)
            if isFirst:
                if isClarification:
                    prompt = get_clarification_prompt(user_utterance=response, trigger_action_current=str_trigger_action_current)
                else: 
                    prompt = get_prompt(isFirst=True, trigger_action_current=str_trigger_action_current, trigger_action_past = "")
            else:
                if isClarification:
                    prompt = get_clarification_prompt(user_utterance=response, trigger_action_current=str_trigger_action_current)
                else:
                    prompt = get_prompt(isFirst=False, trigger_action_current=str_trigger_action_current,
                                    trigger_action_past=str_trigger_action_past, old_response=old_response)

            # Chiamata al modello per la i-esima volta
            response = str(model.respond(prompt, config={"temperature": 0.8}))
            user_utterance = get_system_user_utterances(response=response)

            # current_text += f"User utterance {i}:" + user_utterance + "\n"

    if not validation_result:
        # se dopo tre tentativi il risultato della validazione non è corretto, allora si genera la risposta con il prompt di correzione
        # print("Correzione della risposta in corso...")
        # current_text += "Correzione della risposta in corso...\n"
        
        if not isFirst:
            system_utterance = get_system_user_utterances(user = False, response = response)

            correction_prompt = get_utterance_correction_prompt(system_utterance = system_utterance, trigger_action_current = str_trigger_action_current, isFirst = isFirst)
            correction_response = str(model.respond(correction_prompt, config={"temperature": 0.6}))

            current_text += "- System: " + system_utterance + "\n" + correction_response + "\n"
            old_response = "- System: " + system_utterance + "\n" + correction_response
        else:
            correction_prompt = get_utterance_correction_prompt(system_utterance = '', trigger_action_current = str_trigger_action_current, isFirst = isFirst)
            correction_response = str(model.respond(correction_prompt, config={"temperature": 0.6}))

            current_text += correction_response + "\n"
            old_response = correction_response
    else:
        current_text += response
        old_response = response

    return current_text, old_response


def update_bf_error(text: str, bf_current: dict, bf_new: dict) -> dict:
    """
    - text: la stringa contenente 'ERROR:' seguito da coppie chiave: 'valore' o sole chiavi
    - bf_current: dizionario di partenza; ne vengono rimosse le chiavi trovate nel testo
    Restituisce bf_current modificato.
    """
    # Estrai la parte dopo 'ERROR:'
    parts = text.split('ERROR:', 1)
    if len(parts) < 2:
        return bf_current
    error_part = parts[1]

    # Trova tutte le occorrenze di chiave: 'valore' o solo chiave separate da virgola
    # Gruppi: 1=chiave, 2=blocco valore (facoltativo)
    pattern = r"(\w+)(?::\s*('(?:[^']|\\')*'(?:\s*,\s*'(?:[^']|\\')*')*))?"
    matches = re.findall(pattern, error_part)

    # Per ogni coppia, ricostruisci il valore 
    parsed = {}
    for key, val_block in matches:
        key = key.strip()
        if not val_block:
            parsed[key] = None
        else:
            values = re.findall(r"'((?:[^']|\\')*)'", val_block)
            if len(values) > 1:
                parsed[key] = ", ".join(f"'{v}'" for v in values)
            elif len(values) == 1:
                parsed[key] = values[0]
            else:
                parsed[key] = None

    # Determina quali chiavi rimuovere:
    found = [k for k in parsed if k in bf_current]
    if found:
        # Rimuovi solo quelle trovate
        for k in found:
            bf_current.pop(k, None)
    else:
        # Se nessuna trovata, rimuovi tutte le chiavi di bf_new
        for k in bf_new:
            bf_current.pop(k, None)

    return bf_current


def generate_question_and_answer(fields_trigger_action, entry, fields, current_text, bf_current, str_trigger_action_past, old_response, isAction = False, correct = True):
    """
        Metodo per generare question e answer tramite la selezione casuale dagli elementi nella lista 'fields_trigger_action'.
        - fields_trigger_action: campi della regola trigger-action
        - entry: elemento del dataset
        - fields: campi correnti della regola trigger action
        - current_text: testo corrente con le utterance
        - bf_current: belief state corrente
        - str_trigger_action_past: stringa con i campi della regola trigger-action generati all'ultima generazione
        - old_response: risposta precedente
        - isAction: flag per indicare se siamo in fase di generazione della parte action
        - correct: flag per indicare se la risposta è corretta o errata
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
            # current_text += "\nBelief State: " + str(bf_current) + "\nEnd BF\n"

            # se ho l'errore allora devo correggere l'errore e poi 
            if isError:
                # aggiornamento del belief state rimuovendo gli errori generati
                bf_current_error = update_bf_error(response, bf_current, bf_new)
                
                # salvataggio della risposta con errore
                current_text += response
                current_text += "\nBelief State: " + str(bf_current_error) + "\nEnd BF\n"

                # current_text += "Clarification question\n"
                # stringa del prompt corretto 
                prompt = get_clarification_prompt(user_utterance=response, trigger_action_current=str_trigger_action_current)
            
                # Chiamata al modello
                response = str(model.respond(prompt, config={"temperature": 0.6}))

                # current_text += response
                # current_text += "\nBelief State: " + str(bf_current) + "\nEnd BF\n"

                # Validazione della risposta - se l'utterance è corretta
                current_text, old_response = validate_prompt(response, str_trigger_action_current, current_text,
                                                isFirst = False, old_response = old_response, str_trigger_action_past = str_trigger_action_past,
                                                isClarification = True)
            else: 
                # Validazione della risposta - se l'utterance è corretta
                current_text, old_response = validate_prompt(response, str_trigger_action_current, current_text,
                                                isFirst = False, old_response = old_response, str_trigger_action_past = str_trigger_action_past)

            # current_text += response + "\n"
            current_text += "\nBelief State: " + str(bf_current) + "\nEnd BF\n"
            # old_response = response

            str_trigger_action_past = str_trigger_action_current


    return fields, current_text, bf_current, str_trigger_action_past, old_response