import lmstudio as lms
from openai import OpenAI
import json


name_model = "gemma-2-2b-it"

model = lms.llm(name_model)

# Usando l'API gpt4-all
# Token esaurito (DA MODIFICARE)
# client = OpenAI(api_key="g4a-bKeS8JvQiSrnUFyIKKJrYcZNHbuDvNv75pv", base_url="https://api.gpt4-all.xyz/v1")

# def get_response(prompt):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         stream=False,
#         # n = 3
#     )

#     return response

"""
    PROMPT STATICO
"""

prompt_rules ="""
Trigger Action Rules refers to an event-based system. When a specific event occurs, it triggers a predefined action.
This helps connect different services so they can work together without manual effort. Trigger Action Rules refers to an event-based system.
The trigger-action rule is divided into two subparts, trigger and action, both containing channel, title and fields.
The key concepts are:

trigger_channel: an entity providing various services.
trigger_title: a specific functionality or service offered by a trigger_channel.
trigger_fields: predefined type parameters required by a trigger_title to configure the exact behaviour of the event. Each trigger_field has a name and value and may be mandatory or optional.
action_channel: the entity that provides the action service resulting from the trigger.
action_title: a specific action_channel functionality that is executed when the trigger is activated.
action_fields: type parameters required to define the behaviour of the action executed by the action_title.
When the trigger is activated, the system automatically executes the associated action.
"""

prompt_exception = """
In some cases it may occur that trigger_fields and action_fields can be empty. If the fields is empty then the fields_values must also be empty.
So, if trigger_fields = '' then trigger_fields_values = ''.
"""


prompt_example = """## INPUT
# Trigger-action rules
trigger_channel: 'YouTube'
trigger_title: 'New liked video'
trigger_fields: ''
action_channel: 'Facebook Pages'
action_title: 'Create a link post'
action_fields: 'Link URL (Text input > Link), Message (Text input)'

## OUTPUT
trigger_channel: 'YouTube'
trigger_title: 'New liked video'
trigger_fields: ''
trigger_fields_values: ''
action_channel: 'Facebook Pages'
action_title: 'Create a link post'
action_fields: 'Link URL (Text input > Link), Message (Text input)'
action_fileds_values: ['https://www.youtube.com/watch?v=yz_XGeAzn14&rco=1', 'This is my favourite song!!!'']
"""

prompt_end = """
Thus, considering channel, title and fields, for both trigger and action, generates a possible value for fields_values. In particular, the values of trigger_fields_values and action_fields_values must be consistent with trigger_channel, trigger_title, action_channel and action_title, respecting the type given in trigger_fields and action_fields. Furthermore, the values generated must not alter the meaning of the trigger-action rule provided as input.
"""

# Carica il Dataset
with open("dataset/values_prova.json", "r", encoding="ISO-8859-1") as f:
    dataset = json.load(f)


for i, entry in enumerate(dataset):
    # Mappa i campi del JSON ai campi del prompt
    trigger_channel = entry["trigger_channel"]
    trigger_title = entry["trigger_title"]
    trigger_fields = entry["trigger_fields"]
    action_channel = entry["action_channel"]
    action_title = entry["action_title"]
    action_fields = entry["action_fields"]


    prompt_completo = f"""Generates trigger_fields_values and action_fields_values considering the type assumed by trigger_fields and action_fields respectively. The values to be generated must be consistent with the trigger-action rule provided as input. Accordingly, the values of trigger_fields_values and action_fields_values must not alter the meaning of the trigger-action rule.

### RULES 
{prompt_rules}

## EXCEPTION RULES
{prompt_exception}

### EXAMPLE TRIGGER-ACTION RULES
{prompt_example}

---

### CURRENT INPUT
# Trigger-action rules
trigger_channel: '{trigger_channel}'
trigger_title: '{trigger_title}'
trigger_fields: '{trigger_fields}'
action_channel: '{action_channel}'
action_title: '{action_title}'
action_fields: '{action_fields}'

{prompt_end}
    """

    # try:
    #         # print('Producing response...')
    #         response = get_response(prompt_completo)
    #         # print("Pipeline executed successfully.")
    # except Exception as e:
    #         print("Error occurred:")
    #         print(e)

    # new_edus = [c.message.content.strip("'") for c in response.choices]

    # print(new_edus)

    print(f"Regola Trigger-Action {i}\n")

    result = model.respond(prompt_completo)

    
    """
        SALVATAGGIO SU FILE DEL RISULTATO
    """
    with open(f"output_values/{name_model}_output{i}.txt", "w") as file:
        file.write(str(result))

    print(result)