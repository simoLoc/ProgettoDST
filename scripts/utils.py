prompt_prima_utterance_inizio = """Generates a user's utterance, based on the trigger-action rule fields provided as input. 
The utterance must be as human as possible and must be correlated and consistent with the completion of the various fields of the trigger-action rule.
The output must contain user's utterance on completing of the fields provided as input of the trigger-action rule.

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
When the trigger is activated, the system automatically executes the associated action. The trigger_fields and action_fields can be empty, and consequently fields_values are also empty. Therefore, in the output you should not generate utterances that complete these fields. 

Titles depend on the specified channels.
Fields depend on the specified titles and channels.
Fields values depend on the type specified in fields.


### EXAMPLE TRIGGER-ACTION RULES
## INPUT
## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

## OUTPUT
- User: I want you to monitor all new Facebook posts that have a photo and a specific hashtag.

---
"""


### CURRENT INPUT
## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE

prompt_prima_utterance_fine = """
By analysing the trigger action rule fields to be completed provided as input, it generates a user's utterance.
The output must respect the format of the output given in the example.
"""

prompt_incrementale_inizio = """ Generates a question provided by the system and a corresponding response from the user, based on the trigger-action rule fields provided as input.
The system must ask questions that are related to and consistent with the completion of the various fields in the trigger-action rule.
Conversely, the user must provide the values needed to complete the fields.
The output must contain the system's and user's utterance respectively on the completion of the fields provided as input of the trigger-action rule.

### RULES
Trigger Action Rules refers to an event-based system. When a specific event occurs, it triggers a predefined action.
This helps connect different services so they can work together without manual effort. Trigger Action Rules refers to an event-based system.
The trigger-action rule is divided into two subparts, trigger and action, both containing channel, title and fields.
The key concepts are:

trigger_channel: an entity providing various services.
trigger_title: a specific functionality or service offered by a trigger_channel.
trigger_fields: predefined type parameters required by a trigger_title to configure the exact behaviour of the event.
trigger_fields_values: i valori assunti concordanti con il tipo contenuto in trigger_fields.
action_channel: the entity that provides the action service resulting from the trigger.
action_title: a specific action_channel functionality that is executed when the trigger is activated.
action_fields: type parameters required to define the behaviour of the action executed by the action_title.
action_fields_values: i valori assunti concordanti con il tipo contenuto in action_fields.
When the trigger is activated, the system automatically executes the associated action. The trigger_fields and action_fields can be empty, and consequently fields_values are also empty. Therefore, in the output you should not generate utterances that complete these fields.
Titles depend on the specified channels.
Fields depend on the specified titles and channels.
Fields values depend on the type specified in fields.

### EXAMPLE TRIGGER-ACTION RULES
## INPUT
## FIELDS ALREADY COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE]
trigger_fields: 'Hashtag (Text input)''
trigger_fields_values: ''#frase_poderosa'

## OUTPUT

- System: Would you like me to specify an hashtag to add in your Facebook post?
- User: Yes, I would like you to add the hashtag #frase_poderosa.
---

"""





prompt_incrementale_fine = """
By analysing the trigger action rule fields to be completed provided as input, it generates a system question and a user response.
Fields already completed in the trigger-action rule refer to fields already known by the system. These are provided as context for the output to be produced.
The system must not explicitly ask for that field to be completed.
The system question does not have to specify the value of the field, but it should only be contained in the user response.
The output must respect the format of the output given in the example.

"""


def get_prompt(isFirst, trigger_action_current, trigger_action_past):
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