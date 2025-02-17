from autre.outilDebugage import printDebug
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO

from gestionFenetre.creerElementsWidget import *


"""//CHARGER_PHOTO_LOGO
Fonction qui charge l'image du logo de la ligne
@param logoLigne: l'url du logo
@return ImageTk.PhotoImage: l'image du logo
"""
def charger_photo_logo(logoLigne:str):
    if logoLigne == "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png":
        logo_img = Image.open("Icon/Logo_Transilien.png")
    else:
        response = requests.get(logoLigne)
        logo_img = Image.open(BytesIO(response.content))
    logo_img = logo_img.resize((40, 40), Image.LANCZOS)
    return ImageTk.PhotoImage(logo_img)


"""//CREER_WIDGET
Fonction qui crée un widget contenant les informations d'un train
@param parent: le cadre parent
@param logoLigne: l'url du logo de la ligne
@param mission: la mission
@param direction: la direction
@param en_direct: si le train est en direct
@param temps_en_station: le temps en station
@param temps_avant_arrivee: le temps avant l'arrivée
@param voie: la voie
@param temps_arrivee: l'heure d'arrivée
@param widgets_train: la liste des widgets de train
@return cadre: le cadre contenant les informations du train
"""
def creer_widget(parent, logoLigne:str, mission:str, direction:str, en_direct:bool, temps_en_station:str, temps_avant_arrivee:str, voie:str, temps_arrivee:str, widgets_train) -> "ctk.CTkFrame":
    printDebug("Création d'un nouveau widget")
    cadre = ctk.CTkFrame(parent, fg_color='#1a1d3b', corner_radius=20, height=60)
    cadre.pack(padx=5, pady=5, fill='x')
    
    photo_logo = charger_photo_logo(logoLigne)
    creer_etiquette_logo(cadre, photo_logo)
    
    creer_etiquette_mission(cadre, mission)
    creer_etiquette_station(cadre, direction)
    creer_etiquette_temps(cadre, temps_en_station)
    
    cadre.columnconfigure(4, weight=1)
    
    etiquette_restant = creer_etiquette_restant(cadre, temps_avant_arrivee, en_direct)
    creer_etiquette_voie(cadre, voie)
    
    if not isinstance(temps_en_station, str):
        temps_en_station = "0s"
    
    widgets_train.append((cadre, etiquette_restant, temps_arrivee, temps_en_station[:-1]))
    return cadre