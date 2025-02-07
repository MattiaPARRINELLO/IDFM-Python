import json
import re
import datetime
import requests
import tkinter as tk
from dotenv import load_dotenv

load_dotenv()

URLApi = os.getenv("API_URL")
from requests.auth import HTTPBasicAuth
import os


global URLApi, cleAPI
cleAPI = os.getenv("API_KEY")
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
            return {}
        identifiantLigne = identifiantLigne.split(':')[3]
    with open('DataSet/lignes.json', 'r') as file:
        lignes = json.load(file)
        for ligne in lignes:

            if ligne['id_line'] == identifiantLigne:
                if ligne['picto'] == None:
                    ligne['picto'] = {
                        'url' : "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png",
                        'largeur' : 100,
                        'hauteur' : 100,
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



def avoirProchainsDeparts(idStation:str) -> list:
    paternIdStationLong = r'^STIF:StopPoint:Q:\d{5,6}:$'
    paternIdStationSimple = r'^\d{5,6}$'
    if not re.match(paternIdStationLong, idStation):
        if not re.match(paternIdStationSimple, idStation):
            printDebug(f"Le format de l'identifiant de la station n'est pas valide: {idStation}")
            return []
        idStation = f"STIF:StopPoint:Q:{idStation}:"
    printDebug(f"Nouvelle station demandée: {idStation}")
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
    

def formaterProchainsDeparts(data):
    dataRenvoyee = []
    dataPrincipale = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
    identifiantPassage = 0
    for passage in dataPrincipale:
        printDebug("###---Nouveau passage---###")
        enDirect = True
        informationLigne = avoirInformationLigne(passage["MonitoredVehicleJourney"]["LineRef"]["value"])
        tmpArrivee = 0
        if not passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"]:
            passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"] = { "value" : "#"}
        if passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedArrivalTime"):
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
        else:
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedArrivalTime"] or passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"]
            enDirect = False

        #Si la destination du train est la station actuelle, on ne l'affiche pas
        if passage["MonitoredVehicleJourney"]["DestinationName"][0]["value"] == passage["MonitoredVehicleJourney"]["MonitoredCall"]["StopPointName"][0]["value"]:
            printDebug("---Saut du train---")
            printDebug("La destination est la station actuelle")
            printDebug("#####################")
            continue
        
        arriveeTMP = tmpArrivee
        maintenant = datetime.datetime.now(datetime.timezone.utc).isoformat()
        diff = (datetime.datetime.fromisoformat(arriveeTMP) - datetime.datetime.fromisoformat(maintenant)).total_seconds()
        if diff < -120 or diff > 3600 or diff != diff:  # diff != diff checks for NaN
            printDebug("---Saut du train---")
            printDebug("Le train est trop tôt ou trop tard")
            printDebug("#####################")
            continue

        diffMinutes = int(diff / 60)
        diffSecondes = int(diff % 60)
        diff = f"{diffMinutes}m {diffSecondes}s"
        if diff == "NaNm NaNs":
            diff = "unknown"

        if diffMinutes <= 0 and diffSecondes <= 0:
            diff = "🚉 ➡️" + diff

        if not passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"):
            passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"] = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedDepartureTime"]

        depart = datetime.datetime.fromisoformat(passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"])
        tempsEnStation = depart - datetime.datetime.fromisoformat(arriveeTMP)
        tempsEnStation = str(int(tempsEnStation.total_seconds())) + "s"
        
        if tempsEnStation == "0s" or tempsEnStation == "NaNs":
            tempsEnStation = None

        misson = ""
        if len(passage["MonitoredVehicleJourney"]["JourneyNote"]) == 0:
            printDebug("Aucune mission trouvée")
        else:
            misson = passage["MonitoredVehicleJourney"]["JourneyNote"][0]["value"]

        passageFormate = {
            "id": identifiantPassage,
            "ligne": informationLigne,
            "direction": passage["MonitoredVehicleJourney"]["DestinationName"][0]["value"],
            "mission": misson,
            "aQuai": passage["MonitoredVehicleJourney"]["MonitoredCall"]["VehicleAtStop"],
            "arriveeEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"],
            "arriveeEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedArrivalTime"],
            "departEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"],
            "departEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedDepartureTime"],
            "statut": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalStatus"],
            "quai": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"]["value"],
            "longueur": passage["MonitoredVehicleJourney"]["VehicleFeatureRef"][0],
            "arriveeDans": diff,
            "arrivalTemp": arriveeTMP,
            "tempsEnStation": tempsEnStation,
            "enDirect": enDirect
        }
        dataRenvoyee.append(passageFormate)
        printDebug("ID: " + str(identifiantPassage))
        printDebug("Direction: " + passageFormate["direction"])
        printDebug("Misson : " + passageFormate["mission"])
        printDebug("Arrive dans : " + passageFormate["arriveeDans"])
        printDebug("Quai : " + passageFormate["quai"])
        printDebug("Temps en station : " + passageFormate["tempsEnStation"])
        printDebug("Ligne : " + passageFormate['ligne']["nom"])
        printDebug("##############")
        identifiantPassage += 1

    dataRenvoyee.sort(key=lambda x: x["arrivalTemp"])
    return dataRenvoyee







#### Create an interface to display the data ####








