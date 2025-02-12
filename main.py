import json
import re
import datetime
import requests
from tkinter import ttk
import customtkinter as ctk
import tkinter as tk
from dotenv import load_dotenv
from PIL import Image, ImageTk
from io import BytesIO

load_dotenv()
train_widget = []

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
        # Remove duplicates based on 'zdaid'
        seen_zdaid = set()
        unique_arrets = []
        for arret in arrets:
            if arret['zdaid'] not in seen_zdaid:
                unique_arrets.append(arret)
                seen_zdaid.add(arret['zdaid'])
        arrets = unique_arrets
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
        if not passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ArrivalPlatformName"):
            passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"] = { "value" : "#"}
        if passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedArrivalTime"):
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
        else:
            if passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedArrivalTime"):
                tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedArrivalTime"]
            elif passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"):
                tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"]
            elif passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedDepartureTime"):
                tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedDepartureTime"]
            else:
                printDebug("Aucune information sur l'heure d'arrivée")
                continue
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
            "aQuai": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("VehicleAtStop"),
            "arriveeEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedArrivalTime"),
            "arriveeEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedArrivalTime"),
            "departEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"),
            "departEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedDepartureTime"),
            "statut": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ArrivalStatus"),
            "quai": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"]["value"],
            "longueur": passage["MonitoredVehicleJourney"]["VehicleFeatureRef"][0],
            "arriveeDans": diff,
            "arrivalTemp": arriveeTMP,
            "tempsEnStation": tempsEnStation,
            "enDirect": enDirect
        }
        dataRenvoyee.append(passageFormate)
        printDebug("ID: " + str(identifiantPassage))
        printDebug("Direction: " + str(passageFormate["direction"]))
        printDebug("Misson : " + str(passageFormate["mission"]))
        printDebug("Arrive dans : " + str(passageFormate["arriveeDans"]))
        printDebug("Quai : " + str(passageFormate["quai"]))
        printDebug("Temps en station : " + str(passageFormate["tempsEnStation"]))
        printDebug("Ligne : " + str(passageFormate['ligne']["nom"]))
        printDebug("##############")
        identifiantPassage += 1

    dataRenvoyee.sort(key=lambda x: x["arrivalTemp"])
    return dataRenvoyee


def update_time():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    time_label.configure(text=now)
    root.after(1000, update_time)




#Creation de la fenêtre principale
# Create a scrollable canvas

ctk.set_appearance_mode("light")
root = ctk.CTk()
root.title('Prochains départs')
root.geometry('1600x900')
root.resizable(False, False)
im = Image.open("Icon/logo.png")
photo = ImageTk.PhotoImage(im)
root.wm_iconphoto(True, photo)

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




def update_suggestions(event):
    suggestions = avoirStations(search_entry.get(), limite=5)
    for widget in suggestion_frame.winfo_children():
        widget.destroy()
    if suggestions:
        suggestion_frame.place(x=search_entry.winfo_x(), y=search_entry.winfo_y() + search_entry.winfo_height())
        for suggestion in suggestions:
            def on_enter(event, label=suggestion['arrname']):
                event.widget.configure(bg="#D3D3D3")
            def on_leave(event, label=suggestion['arrname']):
                event.widget.configure(bg="white")
            def on_click(label=suggestion['arrname']):
                loading_screen = ctk.CTkToplevel(root)
                loading_screen.geometry("300x0")
                loading_screen.title("Chargement..")
                loading_label = ctk.CTkLabel(loading_screen, text="Loading...", font=("Arial", 20, "bold"))
                loading_label.pack(expand=True)
                root.update()

                root.update_idletasks()
                search_entry.delete(0, tk.END)
                search_entry.insert(0, label)
                suggestion_frame.place_forget()
                zdaid = avoirStations(label)[0]['zdaid']
                for widget in display_frame.winfo_children():
                    widget.destroy()
                
                train_widget.clear()
                prochainsDeparts = avoirProchainsDeparts(zdaid)
                prochainsDeparts = formaterProchainsDeparts(prochainsDeparts)
                for depart in prochainsDeparts:
                    create_widget(display_frame, depart['ligne']['image']['url'], depart['mission'], depart['direction'], depart['enDirect'], depart['tempsEnStation'], depart['arriveeDans'], depart['quai'], depart["arrivalTemp"])
                    
                loading_screen.destroy()
                root.after(1000, maj_temps_arrivee)

            suggestion_button = ctk.CTkButton(suggestion_frame, text=suggestion['arrname'], fg_color="white", text_color="black", anchor="w", command=lambda s=suggestion['arrname'], on_click=on_click: on_click(s))
            suggestion_button.pack(fill=ctk.X)
            suggestion_button.bind("<Enter>", on_enter)
            suggestion_button.bind("<Leave>", on_leave)

    else:
        suggestion_frame.place_forget()

search_entry.bind("<KeyRelease>", update_suggestions)

# Frame for search suggestions
suggestion_frame = ctk.CTkFrame(root, fg_color="white")
suggestion_frame.place_forget()


    

def create_widget(parent, logoLigne, mission, direction, enDirect, tempsEnStation, tempsAvantArrivee, voie, tempsArrivee):
    printDebug("Création d'un nouveau widget")
    frame = ctk.CTkFrame(parent, fg_color='#1a1d3b', corner_radius=20, height=60)
    frame.pack(padx=5, pady=5, fill='x')
    
    # Téléchargement de l'image du logo H en ligne
    if logoLigne == "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png":
        logo_img = Image.open("Icon/Logo_Transilien.png")
    else:
        url = logoLigne
        response = requests.get(url)
        logo_img = Image.open(BytesIO(response.content))
    logo_img = logo_img.resize((40, 40), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    
    label_logo = tk.Label(frame, image=logo_photo, bg='#1a1d3b')
    label_logo.image = logo_photo
    label_logo.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    label_mission = ctk.CTkLabel(frame, text=mission, text_color='#6c757d', font=('Arial', 16))
    label_mission.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    
    label_station = ctk.CTkLabel(frame, text=direction, text_color='white', font=('Arial', 20, 'bold'))
    label_station.grid(row=0, column=2, padx=10, pady=5, sticky='w')
    
    label_time = ctk.CTkLabel(frame, text=tempsEnStation, text_color='#6c757d', font=('Arial', 16))
    label_time.grid(row=0, column=3, padx=10, pady=5, sticky='w')

    
    frame.columnconfigure(4, weight=1)  # Pousse les éléments à droite
    
    if enDirect:
        color="#28a745"
    else:
        color="#dc3545"

    label_remaining = ctk.CTkLabel(frame, text=tempsAvantArrivee, text_color=color, font=('Arial', 16, 'bold'), corner_radius=20, fg_color='#1a1d3b', padx=10, pady=5)
    label_remaining.grid(row=0, column=5, padx=10, pady=5, sticky='e')
    
    label_number = ctk.CTkLabel(frame, text=voie, fg_color='white', text_color='black', font=('Arial', 18, 'bold'), width=50, height=50, corner_radius=25)
    label_number.grid(row=0, column=6, padx=10, pady=5, sticky='e')

    if not isinstance(tempsEnStation, str):
        tempsEnStation = "0s" 
    
    train_widget.append((frame, label_remaining, tempsArrivee, tempsEnStation[:-1]))

    return frame


def maj_temps_arrivee():
    printDebug("Mise à jour des temps d'arrivée")
    maintenant = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for widget in train_widget:
        diff = (datetime.datetime.fromisoformat(widget[2]) - datetime.datetime.fromisoformat(maintenant)).total_seconds()
        if diff < -120 or diff > 3600 or diff != diff:
            widget[0].destroy()
            train_widget.remove(widget)
            continue
        
        if diff <= 0:
            diff = diff * -1
            if diff > int(widget[3])+10:
                widget[0].destroy()
                continue
            diff = int(diff)
            diff = "🚉 ➡️" + str(diff)
        else: 
            diffMinutes = int(diff / 60)
            diffSecondes = int(diff % 60)
            diff = f"{diffMinutes}m {diffSecondes}s"

        
        widget[1].configure(text=diff)

    root.after(1000, maj_temps_arrivee)






root.mainloop()