import json

def decode_json_unicode(input_file, output_file):
    try:
        # Lecture du fichier JSON
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Réécriture du fichier avec les caractères décodés
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        print(f"Fichier traité et enregistré dans : {output_file}")
    except Exception as e:
        print(f"Erreur : {e}")

# Exemple d'utilisation
input_file = "yourfile.json"  # Remplace par le chemin de ton fichier JSON
output_file = "DataSet/arrets.json"  # Chemin du fichier de sortie
decode_json_unicode(input_file, output_file)
