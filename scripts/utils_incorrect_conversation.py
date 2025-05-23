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
#   PROMPT PER LA DESCRIZIONE INIZIALE ERRATA
# ----

prompt_prima_utterance_inizio = f"""Generates a user's utterance, based on the trigger-action rule fields provided as input. 
The utterance must be as human as possible and  must not provide the values needed to complete the fields. 
The user's utterance must be missing some or all of the fields required by the system.

{prompt_rules}


### EXAMPLE TRIGGER-ACTION RULES
## INPUT
# FIELDS TO BE NOT COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

# OUTPUT
- User: I want you to monitor all new posts that have a photo and a specific hashtag.


---
"""

prompt_prima_utterance_fine = """
By analysing the trigger action rule fields to be not completed provided as input, it generates a user's utterance.
The user's utterance must be missing some or all of the fieldsto be not completed. Specifically, the utterance may contain synonyms of the missing field or contain no such field.
The error to be generated may relate to all or some of the fields not completed in the trigger action rule. 
The output must respect the format of the output given in the example.
"""


# ----
#   PROMPT PER LE SYSTEM QUESTION E USER RESPONSE ERRATE
# ----

prompt_incrementale_inizio = f""" Generates a question provided by the system and a corresponding response from the user, based on the trigger-action rule fields provided as input. 
The system must ask questions that are related to and consistent with the completion of the various fields in the trigger-action rule.
Conversely, the user response must not provide the values needed to complete the fields. The user response must be missing some or all of the fields required by the system.

{prompt_rules}

### EXAMPLE TRIGGER-ACTION RULES
## INPUT
# FIELDS ALREADY COMPLETED IN THE TRIGGER-ACTION RULE
trigger_fields: 'Hashtag (Text input)'
trigger_fields_values: '#frase_poderosa'

# PREVIOUS UTTERANCES
- System: Would you like me to specify an hashtag to add in your Facebook post?
- User: I would like you to add the hashtag #frase_poderosa.

# FIELDS TO BE NOT COMPLETED IN THE TRIGGER-ACTION RULE
action_channel: 'Twitter'

# OUTPUT
- System: After identifying the posts, what should I do?
- User: I would like to share it on Social Network.

---

"""


prompt_incrementale_fine = """
By analysing the trigger action rule fields to be not completed provided as input, it generates a system question and a user response.
The fields to be not completed in the trigger-action rule may be more than one, in which case both the system question must refer to all the fields to be not completed. 
The user response must be missing some or all of the fields to be not completed. Specifically, the user response may contain synonyms of the missing field or contain no such field.
The error to be generated may relate to all or some of the fields not completed in the trigger action rule.
During generation also considers previous utterances to preserve coherence, as in a human dialogue. 
Fields already completed in the trigger-action rule refer to fields already known by the system. These are provided as context for the output to be produced.
The system must not explicitly ask for that field to be not completed.
The completion of the fields must be contained in the user's response, not in the system's question.
The output must respect the format of the output given in the example.
"""

# ----
#   PROMPT PER LA CLARIFICATION QUESTION - PRIMA UTTERANCE
# ----

prompt_clarification_inizio_prima = f"""
Generates a system question and a user response.
The system question must be a clarification question and the user response must be clear and complete.
Input is provided containing the fields to be completed in the trigger action rule and the user incorrect utterance.
The purpose of the clarification question is to ask for clarification of the fields to be completed in the action activation rule, using the incorrect user utterance provided as context.

{prompt_rules}

### EXAMPLE TRIGGER-ACTION RULES
## INPUT

# FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

# USER INCORRECT UTTERANCE
- User: I want you to monitor all new posts.

# OUTPUT
- System: Ok, but I'm not sure on what to do and which platform to monitor. Could you specify it?
- User: Please look at all my new Facebook posts with a specific hashtag.

---

"""

prompt_clarification_fine_prima = """
By analysing the fields to be completed in the trigger action rule and the user incorrect utterance, generate a system clarification question and a correct user response.
The input contains the fields to be completed in the trigger action rule and the user incorrect utterance. The system question is intended to simulate a clarification question. 
The clarification question consists of asking for more information on the fields to be filled in the trigger action rule, using the user incorrect utterance as context.
The user response must include the fields to be completed in the trigger action rule.
The system must not explicitly ask for that fields to be completed. 
The completion of the fields must be contained in the user's response, not in the system's question.
In the output, the system's question and the user's response must avoid referring to the trigger action rule.
During generation also considers previous incorrect utterances to preserve coherence, as in a human dialogue.
The output must contain the system question and the user response. The clarification question must be a consequence of the user incorrect utterance and must precede the user correct response, as is the example. The output must respect the format of the output given in the example.
"""


# ----
#   PROMPT PER LA CLARIFICATION QUESTION - UTTERANCE SUCCESSIVE
# ----

prompt_clarification_inizio_incrementale = f"""
Generates a system question and a user response that are a clarification question and a correct response respectively. 
Input is provided containing the fields of the trigger action rule to be completed and the system question with the user's incorrect response. 
The clarification question is intended to ask for clarification of the fields not completed by the incorrect response provided as input. 

{prompt_rules}

### EXAMPLE TRIGGER-ACTION RULES
## INPUT

# FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
trigger_channel: 'Facebook'
trigger_title: 'New photo post by you with hashtag'

# PREVIOUS INCORRECT UTTERANCES
- System: To post the photo on Twitter, what do you want that I must monitor?
- User: I want you to monitor all new posts.

# OUTPUT
- System: Ok, but I'm not sure on what to do and which platform to monitor. Could you specify it?
- User: Please look at all my new Facebook posts with a specific hashtag.

---

"""

prompt_clarification_fine_incrementale = """
By analysing the fields of the trigger action rule to be completed and the system question with the user's incorrect response, generate a clarification question and a correct user response.
The clarification question is intended to ask for clarification of the trigger action rule to be completed, that are not completed in the user incorrect utterance.
During generation also considers previous incorrect utterances to preserve coherence, as in a human dialogue. 
Incorrect previous utterances may also contain only the user's utterance, but the output must contain the system's clarification question and the user's utterance containing all fields to be completed.
The system's question must use as context only the previous incorrect utterances contained in the current input. The user's response must contain all fields to be completed in the trigger action rule. 
The system must not explicitly ask for that fields to be completed.  
The completion of the fields must be contained in the user's response, not in the system's question.
The system's question and the user's response must avoid referring to the trigger action rule.
The output must respect the format of the output given in the example. The output must contain the system's question and the user's response.
"""



def get_incorrect_prompt(isFirst, trigger_action_current, trigger_action_past, old_response = ""):
    if isFirst:
        current_input = f"""
### CURRENT INPUT
## FIELDS TO BE NOT COMPLETED IN THE TRIGGER-ACTION RULE
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

## FIELDS TO BE NOT COMPLETED IN THE TRIGGER-ACTION RULE
{trigger_action_current}
"""
        prompt_inizio = prompt_incrementale_inizio
        prompt_fine = prompt_incrementale_fine


    return prompt_inizio + current_input + prompt_fine




def get_clarification_prompt(user_utterance, trigger_action_current, isFirst = False):

    if isFirst:
        current_input = f"""
    ### CURRENT INPUT

    ## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
    {trigger_action_current}

    ## USER INCORRECT UTTERANCE
    {user_utterance}

    """
        prompt_inizio = prompt_clarification_inizio_prima
        prompt_fine = prompt_clarification_fine_prima
    else:
        current_input = f"""
    ### CURRENT INPUT

    ## FIELDS TO BE COMPLETED IN THE TRIGGER-ACTION RULE
    {trigger_action_current}

    ## PREVIOUS INCORRECT UTTERANCES
    {user_utterance}

    """
        prompt_inizio = prompt_clarification_inizio_incrementale
        prompt_fine = prompt_clarification_fine_incrementale
    

    return prompt_inizio + current_input + prompt_fine

