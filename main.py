import datetime

#Ce script crée une interface graphique pour afficher les prochains départs de trains en utilisant la bibliothèque customtkinter (ctk).

import requests
from tkinter import ttk
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from debugtool import printDebug
from lecture_fichiers_JSON import avoir_stations
from traitementDonnee import formater_prochains_departs
from appelAPI import avoirProchainsDeparts

train_widget = []


"""//UPDATE_TIME//
Fonction qui permet de mettre à jour l'heure affichée dans la fenêtre
@param root: La fenêtre principale
@param time_label: Le label qui affiche l'heure
@return None
"""
def update_time(root, time_label) -> None: 
    if not root.winfo_exists():
        return
    now = datetime.datetime.now().strftime("%H:%M:%S")
    time_label.configure(text=now)
    root.after(1000, update_time, root, time_label)

"""//CREER_FENETRE_PRINCIPALE//
Fonction qui permet de créer la fenêtre principale
@return root, search_entry, suggestion_frame, display_frame
"""
def creer_fenetre_principale():
    # Creation de la fenêtre principale
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title('Prochains départs')
    root.geometry('1600x900')
    root.resizable(False, False)

    # Icone de la fenêtre
    im = Image.open("Icon/logo.png")
    photo = ImageTk.PhotoImage(im)
    root.wm_iconphoto(True, photo)

    # Cadre supperieur
    header_frame = ctk.CTkFrame(root, fg_color="white")
    header_frame.pack(fill=ctk.X)

    # Label de la ville
    time_label = ctk.CTkLabel(header_frame, text="--:--:--", font=("Arial", 30, "bold"), fg_color="#7B8E94", corner_radius=5, text_color="white")
    time_label.pack(side=ctk.LEFT, padx=10, pady=5)
    update_time(root, time_label)

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

    # Frame for search suggestions
    suggestion_frame = ctk.CTkFrame(root, fg_color="white")
    suggestion_frame.place_forget()
    search_entry.bind("<KeyRelease>", lambda event: update_suggestions())

    return root, search_entry, suggestion_frame, display_frame

root, search_entry, suggestion_frame, display_frame = creer_fenetre_principale()

"""//UPDATE_SUGGESTIONS//
Fonction qui permet de mettre à jour les suggestions de stations en fonction de l'entrée de recherche
@return None
"""
def update_suggestions():
    suggestions = avoir_stations(search_entry.get(), limite=5)
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
                zdaid = avoir_stations(label)[0]['zdaid']
                for widget in display_frame.winfo_children():
                    widget.destroy()
                
                train_widget.clear()
                prochainsDeparts = avoirProchainsDeparts(zdaid)
                prochainsDeparts = formater_prochains_departs(prochainsDeparts)
                for depart in prochainsDeparts:
                    create_widget(display_frame, depart['ligne']['image']['url'], depart['mission'], depart['direction'], depart['enDirect'], depart['tempsEnStation'], depart['arriveeDans'], depart['quai'], depart["arrivalTemp"],train_widget)
                    
                loading_screen.destroy()
                root.after(1000, lambda: maj_temps_arrivee())

            suggestion_button = ctk.CTkButton(suggestion_frame, text=suggestion['arrname'], fg_color="white", text_color="black", anchor="w", command=lambda s=suggestion['arrname'], on_click=on_click: on_click(s))
            suggestion_button.pack(fill=ctk.X)
            suggestion_button.bind("<Enter>", on_enter)
            suggestion_button.bind("<Leave>", on_leave)

    else:
        suggestion_frame.place_forget()

"""//MAJ_TEMPS_ARRIVEE//
Fonction qui permet de mettre à jour les temps d'arrivée des trains affichés
@return None
"""
def maj_temps_arrivee():
    printDebug("Mise à jour des temps d'arrivée")
    maintenant = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for widget in train_widget:
        diff = (datetime.datetime.fromisoformat(widget[2]) - datetime.datetime.fromisoformat(maintenant)).total_seconds()
        if diff < -120 or diff > 3600 or diff != diff: # Si le temps d'arrivée est invalide ou dépassé alors on supprime le widget
            widget[0].destroy()
            train_widget.remove(widget)
            continue
        
        if diff <= 0: # Si le train est en station alors on affiche le temps en station
            diff = diff * -1
            if diff > int(widget[3])+10: 
                widget[0].destroy()
                continue
            diff = int(diff)
            diff = "🚉 ➡️" + str(diff)
        else: # Sinon on affiche le temps avant l'arrivée
            diffMinutes = int(diff / 60)
            diffSecondes = int(diff % 60)
            diff = f"{diffMinutes}m {diffSecondes}s"

        widget[1].configure(text=diff) # On met à jour le label du temps restant

    root.after(1000, maj_temps_arrivee) # On rappelle la fonction toutes les secondes

"""//CREATE_WIDGET//
Fonction qui permet de créer un widget pour afficher les informations d'un train
@param parent: Le widget parent dans lequel le widget de train sera ajouté
@param logoLigne: URL du logo de la ligne de train
@param mission: Nom de la mission du train
@param direction: Direction du train
@param enDirect: Booléen indiquant si le train est en direct
@param tempsEnStation: Temps que le train passera en station
@param tempsAvantArrivee: Temps avant l'arrivée du train
@param voie: Voie du train
@param tempsArrivee: Heure d'arrivée du train
@param train_widget: Liste des widgets de train
@return Le widget de train créé
"""
def create_widget(parent, logoLigne, mission, direction, enDirect, tempsEnStation, tempsAvantArrivee, voie, tempsArrivee, train_widget):
    printDebug("Création d'un nouveau widget")
    frame = ctk.CTkFrame(parent, fg_color='#1a1d3b', corner_radius=20, height=60) # Création du cadre pour le train
    frame.pack(padx=5, pady=5, fill='x') # Ajout du cadre dans le parent
    
    # Si la ligne n'a pas de logo (vérifie si la valeur par défaut à été envoyée), alors on utilise un logo par défaut
    if logoLigne == "https://upload.wikimedia.org/wikipedia/fr/thumb/f/f3/Logo_Transilien_%28RATP%29.svg/1024px-Logo_Transilien_%28RATP%29.svg.png":
        logo_img = Image.open("Icon/Logo_Transilien.png")
    else: # Sinon on télécharge le logo
        url = logoLigne
        response = requests.get(url)
        logo_img = Image.open(BytesIO(response.content))
    
    # On redimensionne le logo
    logo_img = logo_img.resize((40, 40), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)

    # Met en place le logo
    label_logo = tk.Label(frame, image=logo_photo, bg='#1a1d3b')
    label_logo.image = logo_photo
    label_logo.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    # Met en place la mission du train
    label_mission = ctk.CTkLabel(frame, text=mission, text_color='#6c757d', font=('Arial', 16))
    label_mission.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    
    # Met en place la destination du train
    label_station = ctk.CTkLabel(frame, text=direction, text_color='white', font=('Arial', 20, 'bold'))
    label_station.grid(row=0, column=2, padx=10, pady=5, sticky='w')
    
    # Met en place le temps en station du train
    label_time = ctk.CTkLabel(frame, text=tempsEnStation, text_color='#6c757d', font=('Arial', 16))
    label_time.grid(row=0, column=3, padx=10, pady=5, sticky='w')
    
    # Pousse les éléments à droite
    frame.columnconfigure(4, weight=1) 
    
    # Si le train est en direct alors on défini la couleur du texte en vert, sinon en rouge  
    if enDirect:
        color="#28a745"
    else:
        color="#dc3545"

    # Met en place le temps avant l'arrivée du train
    label_remaining = ctk.CTkLabel(frame, text=tempsAvantArrivee, text_color=color, font=('Arial', 16, 'bold'), corner_radius=20, fg_color='#1a1d3b', padx=10, pady=5)
    label_remaining.grid(row=0, column=5, padx=10, pady=5, sticky='e')
    
    # Met en place la voie du train
    label_number = ctk.CTkLabel(frame, text=voie, fg_color='white', text_color='black', font=('Arial', 18, 'bold'), width=50, height=50, corner_radius=25)
    label_number.grid(row=0, column=6, padx=10, pady=5, sticky='e')

    # Si le temps d'arrivée est invalide alors on le remplace par 0s
    if not isinstance(tempsEnStation, str):
        tempsEnStation = "0s" 
    
    # On ajoute le widget de train à la liste des widgets
    train_widget.append((frame, label_remaining, tempsArrivee, tempsEnStation[:-1]))

    return frame


# On affiche la fenêtre
root.mainloop()