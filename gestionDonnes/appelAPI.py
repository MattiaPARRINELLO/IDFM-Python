from autre.outilDebugage import printDebug
import requests
import json
from dotenv import load_dotenv
import os
import re


# Utilisation de .env pour récupere la clé API
load_dotenv()
global URLApi, cleAPI
cleAPI = os.getenv("API_KEY")

URLApi = "https://prim.iledefrance-mobilites.fr/marketplace"

"""//AVOIR_PROCHAINS_DEPARTS//
Fonction qui permet d'avoir les prochains départs d'une station
@param idStation : identifiant de la station qui respecte le format donné par la documentation soit xxxxx(x) ou STIF:StopPoint:Q:xxxxx(x):
@return data : données des prochains départs
"""
def avoirProchainsDeparts(idStation:str) -> list:
    #Verifie si idStation respecte le format de l'identifiant de la station et le corrige si necessaire
    paternIdStationLong = r'^STIF:StopArea:SP:\d{5,6}:$'
    paternIdStationSimple = r'^\d{5,6}$'
    if not re.match(paternIdStationLong, idStation):
        if not re.match(paternIdStationSimple, idStation):
            printDebug(f"Le format de l'identifiant de la station n'est pas valide: {idStation}")
            return []
        idStation = f"STIF:StopArea:SP:{idStation}:"
    
    printDebug(f"Nouvelle station demandée: {idStation}")
    #Requete API
    url = f"{URLApi}/stop-monitoring?MonitoringRef={idStation}"
    headers = {
        'Accept': 'application/json',
        'apikey': cleAPI
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        printDebug(f"Erreur lors de la requête API: {response.status_code}")
        return []
    data = response.content
    
    data = json.loads(data)
    return data