import lmstudio as lms
import json
from tqdm import tqdm
import os


name_model = "gemma-3-12b-it"

model = lms.llm(name_model)

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
The trigger_fields and action_fields contain the type of data to be generated. In addition to the type, they may have a specific format, which is preceded by the symbol “>”. In this case, the data to be generated must also respect the specific format.
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
action_fields_values: 'https://www.youtube.com/watch?v=yz_XGeAzn14&rco=1', 'This is my favourite song!!!'
"""

prompt_end = """
Thus, considering channel, title and fields, for both trigger and action, generates a possible value for fields_values, maintaining the same format as the Output of the Example. In particular, the values of trigger_fields_values and action_fields_values must be consistent with trigger_channel, trigger_title, action_channel and action_title, respecting the type given in trigger_fields and action_fields. Furthermore, the values generated must not alter the meaning of the trigger-action rule provided as input. Furthermore, the data to be generated must be as if written by a human, i.e. the field to be generated must appear as real as possible. For example, when considering a URL, a fictitious URL must be generated that looks as real as possible.
"""

# Carica il Dataset
with open("dataset/values_prova.json", "r", encoding="ISO-8859-1") as f:
    dataset = json.load(f)


for i, entry in enumerate(tqdm(dataset, total=len(dataset))):
    # Mappa i campi del JSON ai campi del prompt
    trigger_channel = entry["trigger_channel"]
    trigger_title = entry["trigger_title"]
    trigger_fields = entry["trigger_fields"]
    action_channel = entry["action_channel"]
    action_title = entry["action_title"]
    action_fields = entry["action_fields"]


    prompt_completo = f"""Generates trigger_fields_values and action_fields_values considering the type assumed by trigger_fields and action_fields respectively. The values to be generated must be consistent with the trigger-action rule provided as input. Accordingly, the values of trigger_fields_values and action_fields_values must not alter the meaning of the trigger-action rule. The values to be generated must be as real as possible, simulating human ones. In particular, inside fields_values there must be no fields left to fill in.

### RULES 
{prompt_rules}

## EXCEPTION RULES
{prompt_exception}

### EXAMPLE
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

    result = model.respond(prompt_completo)

    
    """
        SALVATAGGIO SU FILE DEL RISULTATO
    """
    # Percorso del file
    file_path = f"output_values/{name_model}/output{i}.txt"

    # Crea la directory se non esiste
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Scrivi il file
    with open(file_path, "w") as file:
        file.write(str(result))