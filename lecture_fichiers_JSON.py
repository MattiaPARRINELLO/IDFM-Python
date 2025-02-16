from debugtool import printDebug
import json
import re

#Ce script contient les fonctions qui permettent de lire et traiter les fichiers JSON

"""//AVOIR_STATIONS//
Fonction qui permet de trouver les stations d'une ville
@param nomVille : nom de la ville
@param limite : nombre maximum de stations à retourner
@return arrets : liste des stations trouvées
"""
def avoir_stations(nomVille:str, limite = 0) -> list:
    with open('DataSet/arrets.json', 'r') as file: #Ouverture du fichier JSON
        arrets = json.load(file)
        arrets = [arret for arret in arrets if nomVille.lower() in arret['arrname'].lower()] #Filtrer les stations par nom de ville
        arrets.sort(key=lambda arret: arret['arrname'].lower().index(nomVille.lower())) #Trier les stations par nom de ville
        
        #Si aucun arrêt n'est trouvé, on retourne une liste vide
        if len(arrets) == 0:
            printDebug(f"Aucun arrêt trouvé pour la recherche '{nomVille}'")
            return []
        printDebug(f"{len(arrets)} arrêts trouvés pour la recherche '{nomVille}'")

        # Retire les doublons en se basant sur le zdaid
        zdaid_dejavu = set()
        unique_arrets = []
        for arret in arrets:
            if arret['zdaid'] not in zdaid_dejavu:
                unique_arrets.append(arret)
                zdaid_dejavu.add(arret['zdaid'])
        arrets = unique_arrets
        return arrets[:limite] if limite > 0 else arrets
    

"""//AVOIR_INFORMATIONS_LIGNE//
Permet d'avoir des information sur une ligne a partir de son identifiant de station 
@param identifiantLigne : identifiant de ligne suivant le format de la documentation : xxxxx ou STIF:Line::Cxxxxx
@return returnData : dictionnaire contenant diverses informations sur une ligne
"""
def avoir_information_ligne(identifiantLigne:str) -> dict:
    #Verifie si identifiantLigne respecte l'un des deux formats de l'identifiant et le corrige si necessaire
    paternIdLigneSimple = r'^C\d{5}$'
    paternIdLigneLong = r'^STIF:Line::C\d{5}:$'
    if not re.match(paternIdLigneSimple, identifiantLigne):
        if not re.match(paternIdLigneLong, identifiantLigne):
            printDebug(f"Le format de l'identifiant de la ligne n'est pas valide: {identifiantLigne}")
            return {}
        identifiantLigne = identifiantLigne.split(':')[3]

    #Ouverture du fichier JSON
    with open('DataSet/lignes.json', 'r') as file:
        lignes = json.load(file)

        #Pour chaques lignes dans le JSON si l'identifiant de ligne est le bon on retourne les informations de la ligne (formatées)
        for ligne in lignes:
            if ligne['id_line'] == identifiantLigne:
                if ligne['picto'] == None:
                    ligne['picto'] = {
                        'url' : "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png",
                        'width' : 100,
                        'height' : 100,
                        'mimetype' : 'image/png'
                    }
                returnData = {
                    "id": ligne['id_line'] or "unknown",
                    "nom": ligne['name_line'] or "unknown",
                    "couleurAccent": ligne['colourweb_hexa'],
                    "couleurText": ligne['textcolourweb_hexa'],
                    "image": {
                        "url": ligne['picto']['url'],
                        "largeur": ligne['picto']['width'],
                        "hauteur": ligne['picto']['height'],
                        "mimetype": ligne['picto']['mimetype']
                    }
                }
                return returnData
            
        printDebug(f"Aucune ligne trouvée pour l'identifiant '{identifiantLigne}'")
        return {}