import json
import re
import datetime
import requests
<<<<<<< HEAD
import tkinter as tk
from requests.auth import HTTPBasicAuth


global URLApi, cleAPI
cleAPI = "GqB36rlloXKfqxg90Oq1kMKvmi6NZggR"
=======
from tkinter import ttk
import customtkinter as ctk
import tkinter as tk
from dotenv import load_dotenv

load_dotenv()

from requests.auth import HTTPBasicAuth
import os


global URLApi, cleAPI
cleAPI = os.getenv("API_KEY")
>>>>>>> 54dd149f470782243d3fb30a8dff2463d7d2dfe3
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


<<<<<<< HEAD




#### Create an interface to display the data ####
=======
def update_time():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    time_label.configure(text=now)
    root.after(1000, update_time)


ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title("Prochains départs")
root.geometry("800x600")
root.resizable(False, False)
root.iconbitmap('src/icon/logo.ico')

#Creation de la fenêtre principale
ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title('Prochains départs')
root.geometry('1600x900')

#Cadre supperieur
header_frame = ctk.CTkFrame(root, fg_color="white")
header_frame.pack(fill=ctk.X)

#Label de la ville
time_label = ctk.CTkLabel(header_frame, text="--:--:--", font=("Arial", 30, "bold"), fg_color="#7B8E94", corner_radius=5, text_color="white")
time_label.pack(side=ctk.LEFT, padx=10, pady=5)
update_time()

# Titre
title_label = ctk.CTkLabel(header_frame, text="Next Trains", font=("Arial", 25, "bold"), fg_color="white", text_color="#728387")
title_label.pack(side=ctk.LEFT, padx=20)

# Label Voie
voie_label = ctk.CTkLabel(header_frame, text="Voie", font=("Arial", 25, "bold"), fg_color="#0E1436", text_color="white", corner_radius=5)
voie_label.pack(side=ctk.RIGHT, padx=10)

# Champ de recherche pour la station
search_entry = ctk.CTkEntry(header_frame, width=200, placeholder_text="Enter a station")
search_entry.pack(side=ctk.RIGHT, padx=10)

# Zone d'affichage des horaires
display_frame = ctk.CTkFrame(root, fg_color="#C0C0C0")
display_frame.pack(fill=ctk.BOTH, expand=True)



root.mainloop()





>>>>>>> 54dd149f470782243d3fb30a8dff2463d7d2dfe3








