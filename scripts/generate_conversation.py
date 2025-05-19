from copy import copy
import  random
import json
from tqdm import tqdm
import lmstudio as lms
from utils_correct_conversation import *
from utils_incorrect_conversation import *
from utils_generate_question_answer import validate_prompt, generate_question_and_answer, update_bf_error
import os
import ast
import json
import re
from collections import OrderedDict


def count_fields(field_str):
    """
        Metodo che conta il numero di elementi presenti nei fields
    """
    if isinstance(field_str, str) and field_str.strip():
        return len([item.strip() for item in field_str.strip('"').split(',') if item.strip()])
    return 0



def generate_conversation(entry, correct = False):
    """
        - entry: la regola trigger-action presente nel dataset
        - correct: un bool che consente di valutare se la generazione ha o meno l'errore
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
        current_text += "\nBelief State: " + str(bf_current) + "\nEnd BF\n"

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


# def extract_utterances(conversation: str) -> str:
#     """
#         Cattura righe con - System:, - User:, oppure Belief State: {...}
#     """
#     pattern = re.compile(
#         r'''(?mxs)                          # MULTILINE, VERBOSE, DOTALL
#         ^- User:                            # riga che inizia con "- User:"
#         [\s\S]+?                            # qualunque carattere (inclusi \n), min-greedy
#         (?=                                 # fino a una delle due condizioni seguenti:
#         \r?\n- System:                   #    una nuova riga "- System:"
#         | \r?\nBelief\ State:              #  o direttamente la riga "Belief State:"
#         )
#         (?:                                 # blocco opzionale per il System
#         \r?\n- System:                    # riga "- System:"
#         [\s\S]+?                          # qualsiasi contenuto fino a...
#         (?=\r?\nBelief\ State:)          # ...la riga "Belief State:"
#         )?
#         \r?\nBelief\ State:\ \{             # inizio del blocco dati
#         [\s\S]+?                            # tutto il contenuto interno
#         \}\r?\n                             
#         End\ BF\r?\n                        # fine del blocco
#         ''',
#         flags=re.MULTILINE | re.DOTALL | re.VERBOSE
#     )

#     seen = OrderedDict()
#     for match in pattern.finditer(conversation):
#         line = match.group().strip()
#         if line not in seen:
#             seen[line] = None

#     return '\n\n'.join(seen.keys())


def extract_utterances(conversation: str) -> str:
    """
    Estrae blocchi di dialogo che seguono esattamente una di queste strutture:
      1) '- User:' seguito da 'Belief state:' e 'End BF'
      2) '- System:' + '- User:' seguito da 'Belief state:' e 'End BF'
    Ogni blocco termina con la riga 'End BF'.
    Restituisce i blocchi nell'ordine di apparizione, separati da due newline.
    """
    pattern = re.compile(
        r'''
        ^[ \t]*- User:.*?                # Inizio con '- User:' (obbligatorio)
        (?:\r?\n[ \t]*- System:.*?)*?    # Opzionale '- System:' subito dopo
        \r?\n[ \t]*Belief\ State:.*?     # Riga 'Belief State:' obbligatoria
        (?:\r?\n.*?)*?                   # Righe intermedie qualsiasi
        \r?\n[ \t]*End\ BF[ \t]*$        # Riga finale 'End BF'
        ''', re.MULTILINE | re.DOTALL | re.VERBOSE | re.IGNORECASE)

    blocks = [m.group().strip() for m in pattern.finditer(conversation)]
    return "\n\n".join(blocks)



def parse_conversation_to_json(text: str, id: int) -> list:
    """
    Estrae dai blocchi separati da una riga vuota le parti:
    - righe che iniziano con "- Ruolo: testo"
    - la riga "Belief State: {…} ... End BF"
    e restituisce un JSON indentato.
    """
    blocks = re.split(r'\n\s*\n', text.strip())
    conversation = []

    for block in blocks:
        entry = {}

        # Estrai tutte le linee "- Ruolo: testo"
        for role, utterance in re.findall(r'^- (\w+): (.+)$', block, re.MULTILINE):
            entry[role] = utterance.strip()

        # Estrai il dizionario della Belief State (multiline fino a End BF)
        match = re.search(r"Belief State:\s*(\{[\s\S]*?\})\s*End\ BF", block)
        if match:
            belief_state = ast.literal_eval(match.group(1))
            entry['Belief State'] = belief_state

        # Aggiungi all’elenco solo se abbiamo trovato almeno un ruolo
        if entry:
            conversation.append(entry)

    return {"id": id, "dialogue": conversation}


def save_to_json_lines(data, filename):
    with open(filename, 'a', encoding='utf-8') as f:
        for entry in data:
            json_line = json.dumps(entry, ensure_ascii=False)
            f.write(json_line + '\n')



if __name__ == "__main__":

    name_model = "gemma-3-27b-it"
    model = lms.llm(name_model)

    # file_path_correct = "dataset/incremental_conversation_correct.jsonl"
    # file_path_incorrect = "dataset/incremental_conversation_incorrect.jsonl"
    

    # with open("dataset/dataset_train.json", "r", encoding="utf-8") as f:
    #     dataset = json.load(f)

    file_path_correct = "dataset/prova_correct.jsonl"
    file_path_incorrect = "dataset/prova_incorrect.jsonl"
    

    with open("dataset/prova.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    for i, entry in enumerate(tqdm(dataset, total=len(dataset))):
        
        correct_conversation = generate_conversation(entry, correct = True)
        incorrect_conversation = generate_conversation(entry, correct = False)

        # estrazione solo utterance 
        correct_conversation = extract_utterances(correct_conversation)
        incorrect_conversation = extract_utterances(incorrect_conversation)


        """
            SALVATAGGIO DEL JSONL
        """

        json_correct = parse_conversation_to_json(correct_conversation, i)
        json_incorrect = parse_conversation_to_json(incorrect_conversation, i)

        save_to_json_lines([json_correct], file_path_correct)
        save_to_json_lines([json_incorrect], file_path_incorrect)

        # Percorso del file
        # file_path = f"output_2conversazioni/{name_model}/output{i}.txt"

        # Crea la directory se non esiste
        # os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Scrivi il file
        # with open(file_path, "w", encoding="utf-8") as file:
        #     file.write(str(conversation))

        