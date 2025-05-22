# ----
#   RULES DELLE TRIGGER-ACTION RULES
# ----

prompt_rules = """
### RULES
Trigger Action Rules refers to an event-based system. When a specific event occurs, it triggers a predefined action.
This helps connect different services so they can work together without manual effort. Trigger Action Rules refers to an event-based system.
The trigger-action rule is divided into two subparts, trigger and action, both containing channel, title and fields.
The key concepts are:
- trigger_channel: an entity providing various services.
- trigger_title: a specific functionality or service offered by a trigger_channel.
- trigger_fields: predefined type parameters required by a trigger_title to configure the exact behaviour of the event.
- trigger_fields_values: i valori assunti concordanti con il tipo contenuto in trigger_fields.
- action_channel: the entity that provides the action service resulting from the trigger.
- action_title: a specific action_channel functionality that is executed when the trigger is activated.
- action_fields: type parameters required to define the behaviour of the action executed by the action_title.
- action_fields_values: i valori assunti concordanti con il tipo contenuto in action_fields.
When the trigger is activated, the system automatically executes the associated action. The trigger_fields and action_fields can be empty, and consequently fields_values are also empty. Therefore, in the output you must not generate utterances that complete these fields. 

Titles depend on the specified channels.
Fields depend on the specified titles and channels.
Fields values depend on the type specified in fields.
"""

# ----
#   PROMPT PER LA DESCRIZIONE INIZIALE
# ----

prompt_prima_utterance_inizio = f"""Generates a user's utterance, based on the trigger-action rule fields provided as input. 
The utterance must be as human as possible and must be correlated and consistent with the completion of the various fields of the trigger-action rule.
The output must contain user's utterance on completing of the fields provided as input of the trigger-action rule.

{prompt_rules}


### EXAMPLE TRIGGER-ACTION RULES
## INPUT
## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

## OUTPUT
- User: I want you to monitor all new Facebook posts that have a photo and a specific hashtag.

---
"""

prompt_prima_utterance_fine = """
By analysing the trigger action rule fields to be completed provided as input, it generates a user's utterance.
The output must respect the format of the output given in the example.
"""


# ----
#   PROMPT PER LE SYSTEM QUESTION E USER RESPONSE
# ----

prompt_incrementale_inizio = f""" Generates a question provided by the system and a corresponding response from the user, based on the trigger-action rule fields provided as input.
The system must ask questions that are related to and consistent with the completion of the various fields in the trigger-action rule.
Conversely, the user must provide the values needed to complete the fields.
The output must contain the system's and user's utterance respectively on the completion of the fields provided as input of the trigger-action rule.

{prompt_rules}

### EXAMPLE TRIGGER-ACTION RULES
## INPUT
## FIELDS ALREADY COMPLETED IN THE TRIGGER-ACTION RULE
trigger_fields: 'Hashtag (Text input)''
trigger_fields_values: ''#frase_poderosa'

## PREVIOUS UTTERANCES

- System: Would you like me to specify an hashtag to add in your Facebook post?
- User: I would like you to add the hashtag #frase_poderosa.

## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
action_channel: 'Twitter'

## OUTPUT

- System: After identifying the posts, what should I do?
- User: I would like to share it on Twitter.

---

"""


prompt_incrementale_fine = """
By analysing the trigger action rule fields to be completed provided as input, it generates a system question and a user response.
The fields to be completed in the trigger-action rule may be more than one, in which case both the system question and the user response must refer to all the fields to be completed.
The 'fields' and 'fields_values' may be empty. If this is the case, you must not complete these fields when generating the system question and a user response.
During generation also considers previous utterances to preserve coherence, as in a human dialogue.
Fields already completed in the trigger-action rule refer to fields already known by the system. These are provided as context for the output to be produced.
The system must not explicitly ask for that field to be completed.
The system question does not have to specify the filling in of all the fields, but it should only be contained in the user response.
The output must respect the format of the output given in the example.

"""

# ----
#   PROMPT PER LA VALIDAZIONE DELLE USER UTTERANCE
# ----

prompt_validazione_inizio = f"""
Evaluates whether the utterance taken as input contains all the required fields of the trigger action rule.
By analysing the trigger action rule and the fields provided, it returns 1 if the utterance contains all the
required fields and 0 otherwise. The output can only be 0 or 1.

{prompt_rules}

### EXAMPLE 1 TRIGGER-ACTION RULES
## INPUT
## UTTERANCE
- User: I want you to monitor all new Facebook posts that have a photo and a specific hashtag.

## FIELDS OF THE TRIGGER-ACTION RULE FOR UTTERANCE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

## OUTPUT
Result: 1


### EXAMPLE 2 TRIGGER-ACTION RULES
## INPUT
## UTTERANCE
- User: Please play my "Cooking Vibes" playlist.

## FIELDS OF THE TRIGGER-ACTION RULE FOR UTTERANCE
action_fields: ''
action_fields_values: ''

## OUTPUT
Result: 0

---

"""

prompt_validazione_fine = """
By analysing the trigger action rule fields and the utterance, it assesses whether or not the utterance
contains all the required fields.
The utterance may also contain other information or a field rephrasement, but the output must be 1 if the utterance contains at least all the required fields and 0 otherwise. 
In the case of trigger_channel and action_channel, you must check that the utterance contains exactly the values of those fields, as in example 1.
In the case of trigger_title and action_title you can ignore the case of the characters in the utterance, as in example 1.
The utterance may contain more information, but this information must not be about completing empty fields. In particular, analyse whether the utterance, for the meaning of the fields provided, contains only such information as in example 2.
The output must respect the format of the output given in the example.
"""

# ----
#   PROMPT PER LA CORREZIONE DELLE USER UTTERANCE A SEGUITO DI 3 VALIDAZIONI NEGATIVE - PRIMA UTTERANCE
# ----

prompt_correction_inizio_prima = f"""
Generates an utterance containing all the fields provided as input.

### EXAMPLE
## INPUT
## FIELDS TO BE COMPLETED IN THE RESPONSE
trigger_fields: 'Hashtag (Text input)''
trigger_fields_values: ''#frase_poderosa'

## OUTPUT
- User: I would like you to add the hashtag #frase_poderosa.
"""

prompt_correction_fine_prima = """
By analysing the fields to be completed in the response, it generates a user response that is consistent with all the fields.
The output must respect the format of the output given in the example.
"""


# ----
#   PROMPT PER LA CORREZIONE DELLE USER UTTERANCE A SEGUITO DI 3 VALIDAZIONI NEGATIVE - SYSTEM E USER UTTERANCE
# ----

prompt_correction_inizio_incrementale = f"""
Generates an utterance containing all the fields provided as input. Through them, the user's utterance
must be an answer consistent with the system's question.

### EXAMPLE
## INPUT
## SYSTEM'S QUESTION
- System: Would you like me to specify an hashtag to add in your Facebook post?

## FIELDS TO BE COMPLETED IN THE RESPONSE
trigger_fields: 'Hashtag (Text input)''
trigger_fields_values: ''#frase_poderosa'

## OUTPUT
- User: I would like you to add the hashtag #frase_poderosa.
"""

prompt_correction_fine_incrementale = """
By analysing the fields to be completed in the response and the system question, it generates a user
response that is consistent with the question and contains all the fields.
The system question can be null, in which case it is sufficient to consider all the fields to be completed in the generated answer.
The output must respect the format of the output given in the example.
"""

def get_prompt(isFirst, trigger_action_current, trigger_action_past, old_response = ""):
    if isFirst:
        current_input = f"""
### CURRENT INPUT
## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
{trigger_action_current}
"""
        prompt_inizio = prompt_prima_utterance_inizio
        prompt_fine = prompt_prima_utterance_fine
    else:
        current_input = f"""
### CURRENT INPUT
## FIELDS ALREADY COMPLETED IN THE TRIGGER-ACTION RULE
{trigger_action_past}

## PREVIOUS UTTERANCES
{old_response}

## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
{trigger_action_current}
"""
        prompt_inizio = prompt_incrementale_inizio
        prompt_fine = prompt_incrementale_fine


    return prompt_inizio + current_input + prompt_fine


def get_prompt_input(lista_elementi, rule):
    output = ""
    bf = dict()
    for item in lista_elementi:
        if item in rule:
            output += f"'{item}': '{rule[item]}' \n"
            bf[item] = rule[item]

    return bf, output

def get_validation_prompt(user_utterance, trigger_action_current):

    current_input = f"""
    ### CURRENT INPUT
    ## UTTERANCE
    {user_utterance}
    ## FIELDS OF THE TRIGGER-ACTION RULE FOR UTTERANCE
    {trigger_action_current}
    """

    prompt_inizio = prompt_validazione_inizio
    prompt_fine = prompt_validazione_fine

    return prompt_inizio + current_input + prompt_fine

def get_utterance_correction_prompt(system_utterance, trigger_action_current, isFirst=False):

    if isFirst:
        current_input = f"""
        ### CURRENT INPUT
        ## FIELDS TO BE COMPLETED IN THE RESPONSE
        {trigger_action_current}
        """
    else:    
        current_input = f"""
        ### CURRENT INPUT
        ## SYSTEM'S QUESTION
        {system_utterance}
        ## FIELDS TO BE COMPLETED IN THE RESPONSE
        {trigger_action_current}
        """
    if isFirst:
        prompt_inizio = prompt_correction_inizio_prima
        prompt_fine = prompt_correction_fine_prima
    else:
        prompt_inizio = prompt_correction_inizio_incrementale
        prompt_fine = prompt_correction_fine_incrementale

    return prompt_inizio + current_input + prompt_fine