import json
from collections import Counter, defaultdict
import random



if __name__ == "__main__":
    with open('dataset/dataset_6k_completo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)


    # Conta frequenze combinate
    combined_counts = Counter()
    for item in data:
        combined_counts[item['trigger_channel']] += 1
        combined_counts[item['action_channel']] += 1

    # Scrivi su file di testo
    output_path = 'channel_frequencies.txt'
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("channel\tfrequency\n")
        for channel, freq in combined_counts.most_common():
            file.write(f"{channel}\t{freq}\n")

    # Conta le occorrenze delle coppie (trigger, action)
    pair_counts = Counter((item['trigger_channel'], item['action_channel']) for item in data)

    # Scrivi su file di testo, ordinato per frequenza decrescente
    output_path = 'trigger_action_pairs_frequencies.txt'
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("trigger_channel\taction_channel\tfrequency\n")
        for (trigger, action), freq in pair_counts.most_common():
            file.write(f"{trigger}\t{action}\t{freq}\n")

    total = sum(pair_counts.values())

    num_dataset_val = 200

    # (count / total) è la percentuale della coppia
    # la percentuale * num_dataset_val consente di calcolare il numero occorrenze di quella coppia
    raw_quota = {pair: (count / total) * num_dataset_val for pair, count in pair_counts.items()}
    # round() per arrotondare ogni quota al più vicino intero.
    quotas = {pair: round(q) for pair, q in raw_quota.items()}

    # Differenza di elementi per aver esattamente num_dataset_val
    diff = num_dataset_val - sum(quotas.values())
    if diff > 0:
        # distribuisci ai più sottostimati in raw_quota
        # raw_quota[p] % 1 è la parte frazionaria della quota originale 
        # si ordina in senso decrescente sulla frazione per preferire le diff con la frazione maggiore 
        for pair in sorted(raw_quota, key=lambda p: raw_quota[p] % 1, reverse=True)[:diff]:
            quotas[pair] += 1
    elif diff < 0:
        # togli ai più sovrastimati
        # raw_quota[p] % 1 è la parte frazionaria della quota originale 
        # si ordina in senso crescente sulla frazione per preferire le diff con la frazione minore
        for pair in sorted(raw_quota, key=lambda p: raw_quota[p] % 1)[:abs(diff)]:
            quotas[pair] -= 1

    # Raggruppa e campiona
    groups = defaultdict(list)
    for item in data:
        groups[(item['trigger_channel'], item['action_channel'])].append(item)

    sample_val = []
    for pair, n in quotas.items():
        items = groups[pair]
        sample_val += items if len(items) <= n else random.sample(items, n)

    # Salva il campione
    with open('dataset/dataset_val.json', 'w', encoding='utf-8') as f:
        json.dump(sample_val, f, ensure_ascii=False, indent=2)

    # Calcola e salva le frequenze delle coppie nel sample
    sample_pair_counts = Counter((item['trigger_channel'], item['action_channel']) for item in sample_val)
    with open('sample_pair_frequencies.txt', 'w', encoding='utf-8') as f:
        f.write("trigger_channel\taction_channel\tfrequency\n")
        for (trigger, action), freq in sample_pair_counts.most_common():
            f.write(f"{trigger}\t{action}\t{freq}\n")


    # salvataggio del dataset di validazione
    with open('dataset/dataset_val.json', 'r', encoding='utf-8') as f:
        to_remove = json.load(f)

    # Filtra rimuovendo tutti gli elementi presenti in datset_val
    filtered = [item for item in data if item not in to_remove]

    # salvataggio del dataset di train
    with open('dataset/dataset_train.json', 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)


    print(f"Rimossi {len(data) - len(filtered)} elementi. Risultato in filtered.json ({len(filtered)} elementi).")

