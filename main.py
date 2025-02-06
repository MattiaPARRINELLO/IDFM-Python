import json
import re

#Permet d'avoir la clé API
#Retourne la clé API
def avoirCleApi() -> str:
    with open('dataSet/apiKey.txt', 'r') as file:
        cleApi = file.read()
    return cleApi

URLApi = "https://prim.iledefrance-mobilites.fr/marketplace"


def printDebug(message:str):
    print(f"DEBUG: {message}")





def avoirStations(nomVille:str, limite = 0) -> list:
    with open('DataSet/arrets.json', 'r') as file:
        arrets = json.load(file)
        # ne garder que les arrets qui contiennent nomVille
        arrets = [arret for arret in arrets if nomVille.lower() in arret['arrname'].lower()]
        # // sort retults by % of match like when the querry is Argenteuil, the first one on result is Argenteuil and then Val d'Argenteuil
        # 
        arrets.sort(key=lambda arret: arret['arrname'].lower().index(nomVille.lower()))
        if len(arrets) == 0:
            printDebug(f"Aucun arrêt trouvé pour la recherche '{nomVille}'")
            return []
        printDebug(f"{len(arrets)} arrêts trouvés pour la recherche '{nomVille}'")
        return arrets[:limite] if limite > 0 else arrets
    

def avoirInformationLigne(identifiantLigne:str) -> dict:
    paternIdLigneSimple = r'^C\d{5}$'
    paternIdLigneLong = r'^STIF:Line::C\d{5}:$'
    if not re.match(paternIdLigneSimple, identifiantLigne):
        if not re.match(paternIdLigneLong, identifiantLigne):
            printDebug(f"Le format de l'identifiant de la ligne n'est pas valide: {identifiantLigne}")
            return None
        identifiantLigne = identifiantLigne.split(':')[3]
    with open('DataSet/lignes.json', 'r') as file:
        lignes = json.load(file)
        for ligne in lignes:
            if ligne['id_line'] == identifiantLigne:
                if ligne['id_line']['picto'] == None:
                    ligne['id_line']['picto'] = {
                        'url' : "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png",
                        'width' : 100,
                        'height' : 100,
                        'mimetype' : 'image/png'
                    }
                returnData = {
                    "id": ligne['id_line'] or "unknown",
                    "name": ligne['name_line'] or "unknown",
                    "accentColor": ligne['colourweb_hexa'],
                    "textColor": ligne['textcolourweb_hexa'],
                    "image": {
                        "url": ligne['id_line']['picto']['url'],
                        "width": ligne['id_line']['picto']['width'],
                        "height": ligne['id_line']['picto']['height'],
                        "mimetype": ligne['id_line']['picto']['mimetype']
                    }
                }
                return returnData
            
        printDebug(f"Aucune ligne trouvée pour l'identifiant '{identifiantLigne}'")
        return None
    




