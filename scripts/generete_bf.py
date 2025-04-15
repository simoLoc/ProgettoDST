import  random

# La strutrigger_titleura deve essere una lista per dare importanza all'ordine
trigger = [['trigger_channel'], ['trigger_channel', 'trigger_title'], ['trigger_channel', 'trigger_title', 'trigger_fields'], ['trigger_channel', 'trigger_title', 'trigger_fields', 'trigger_fields_values']]
action = [['action_channel'], ['action_channel', 'action_title'], ['action_channel', 'action_title', 'action_fields'], ['action_channel', 'action_title', 'action_fields', 'action_fields_values']]
triggerAndAction = [['trigger_channel', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel'], ['trigger_channel', 'trigger_title', 'action_channel', 'action_title']]

isAction = random.choice([0, 1])

print("Genero il primo")
if isAction:
    fields = random.choice(triggerAndAction)
    print(fields)
else:
    fields = random.choice(trigger)
    print(fields)


print("Genero le Trigger")

# Generazione solo delle trigger (prima trigger e poi action)
# devono essere 4 stringhe con 'T' -> cioè i 4 campi della trigger
# while not (len(fields) >= 4 and sum(s.startswith('T') for s in fields) == 4):
while not (sum(s.startswith('T') for s in fields) == 4):
    new_fields = random.choice(trigger)    
    print(f"inizio del ciclo {fields}")
    print(f"Nuova generazione {new_fields}")
    
    if not set(new_fields).issubset(fields):
        new_elements = set(new_fields) - set(fields)
        new_elements = list(new_elements)
        print(f'new_elements {new_elements}')
        fields += new_elements
        
    print(f"NEW {fields}")

    
print("Genero le Action")
while not (sum(s.startswith('A') for s in fields) == 4):
    new_fields = random.choice(action)    
    print(f"inizio del ciclo {fields}")
    print(f"Nuova generazione {new_fields}")
    
    if not set(new_fields).issubset(fields):
        new_elements = set(new_fields) - set(fields)
        new_elements = list(new_elements)
        print(f'new_elements {new_elements}')
        fields += new_elements
        
    print(f"NEW {fields}")


    