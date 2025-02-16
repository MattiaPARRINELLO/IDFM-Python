from debugtool import printDebug
import customtkinter as ctk

from PIL import Image, ImageTk
import tkinter as tk
import requests
from io import BytesIO


"""//CREER_WIDGET//
Crée un widget pour afficher les informations d'un train.
@param parent: Le cadre parent dans lequel le widget sera placé
@param logoLigne: URL de l'image du logo de la ligne
@param mission: Mission du train
@param direction: Direction/nom de la station
@param enDirect: Booléen indiquant si le temps restant est en direct    
@param tempsEnStation: Temps en station
@param tempsAvantArrivee: Temps restant avant l'arrivée
@param voie: Numéro de la voie
@param tempsArrivee: Heure d'arrivée du train
@param train_widget: Liste mutable contenant les widgets de train
@return frame: Le cadre principal du widget
"""
def creer_widget(parent, logoLigne, mission, direction, enDirect, tempsEnStation, 
                  tempsAvantArrivee, voie, tempsArrivee, train_widget) -> ctk.CTkFrame:
    printDebug("Création d'un nouveau widget")
    # Création du cadre principal du widget avec style personnalisé
    frame = ctk.CTkFrame(parent, fg_color='#1a1d3b', corner_radius=20, height=60)
    frame.pack(padx=5, pady=5, fill='x')
    
    # Gestion de l'affichage de l'image du logo de la ligne
    if logoLigne == "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png":
        logo_img = Image.open("Icon/Logo_Transilien.png")
    else:
        response = requests.get(logoLigne)
        logo_img = Image.open(BytesIO(response.content))
    
    # Redimensionnement et conversion de l'image pour Tkinter
    logo_img = logo_img.resize((40, 40), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    
    # Création du widget pour le logo et placement dans le cadre
    label_logo = tk.Label(frame, image=logo_photo, bg='#1a1d3b')
    label_logo.image = logo_photo
    label_logo.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    # Affichage de la mission du train
    label_mission = ctk.CTkLabel(frame, text=mission, text_color='#6c757d', font=('Arial', 16))
    label_mission.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    
    # Affichage de la direction/nom de la station
    label_station = ctk.CTkLabel(frame, text=direction, text_color='white', font=('Arial', 20, 'bold'))
    label_station.grid(row=0, column=2, padx=10, pady=5, sticky='w')
    
    # Affichage du temps en station
    label_time = ctk.CTkLabel(frame, text=tempsEnStation, text_color='#6c757d', font=('Arial', 16))
    label_time.grid(row=0, column=3, padx=10, pady=5, sticky='w')
    
    # Configuration de la colonne pour occuper l'espace restant
    frame.columnconfigure(4, weight=1) 
    
    # Définition de la couleur en fonction de l'état en direct
    color = "#28a745" if enDirect else "#dc3545"
    # Affichage du temps restant avant arrivée avec une couleur conditionnelle
    label_remaining = ctk.CTkLabel(frame, text=tempsAvantArrivee, text_color=color, 
                                   font=('Arial', 16, 'bold'), corner_radius=20, 
                                   fg_color='#1a1d3b', padx=10, pady=5)
    label_remaining.grid(row=0, column=5, padx=10, pady=5, sticky='e')
    
    # Affichage du numéro de la voie dans un style circulaire
    label_number = ctk.CTkLabel(frame, text=voie, fg_color='white', text_color='black', 
                                font=('Arial', 18, 'bold'), width=50, height=50, corner_radius=25)
    label_number.grid(row=0, column=6, padx=10, pady=5, sticky='e')

    # Si la valeur de tempsEnStation n'est pas une chaîne, la définir par défaut à "0s"
    if not isinstance(tempsEnStation, str):
        tempsEnStation = "0s" 
    
    # Ajoute un tuple contenant le cadre, l'étiquette du temps restant, l'heure d'arrivée
    # et la version numérique du temps en station à la liste train_widget
    train_widget.append((frame, label_remaining, tempsArrivee, tempsEnStation[:-1]))
    return frame