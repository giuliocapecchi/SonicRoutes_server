import json
import subprocess
import math

def calcola_media(ampiezze):
    return sum(ampiezze) / len(ampiezze)

def calcola_deviazione_standard(ampiezze, media):
    return math.sqrt(sum((x - media) ** 2 for x in ampiezze) / len(ampiezze))

def calcola_z_score(ampiezza, media, deviazione_standard):
    return (ampiezza - media) / deviazione_standard

def leggi_file_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def calcola_z_scores(json_data):
    ampiezze = [entry['amplitude'] for entry in json_data]
    media = calcola_media(ampiezze)
    deviazione_standard = calcola_deviazione_standard(ampiezze, media)
    
    z_scores = []
    for entry in json_data:
        z_score = calcola_z_score(entry['amplitude'], media, deviazione_standard)
        z_scores.append({
            'startCrossingId': entry['startCrossingId'],
            'endCrossingId': entry['endCrossingId'],
            'z_score': z_score
        })
    
    return z_scores

def salva_file_json(json_data, file_path):
    with open(file_path, 'w') as file:
        json.dump(json_data, file, indent=4)

def main():
    file_input_path = 'data/data.json'
    json_data = leggi_file_json(file_input_path)
    z_scores = calcola_z_scores(json_data)
    
    file_output_path = 'data/z_scores_rumori.json'
    salva_file_json(z_scores, file_output_path)
    
    print(f"Il file con i Z-scores è stato salvato in: {file_output_path}")

if __name__ == "__main__":
    main()
    subprocess.run(['python', 'mapCreator.py'])