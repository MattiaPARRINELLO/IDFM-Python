import customtkinter as ctk
from PIL import Image, ImageTk
import datetime

from windowManager.majSuggestion import maj_suggestions


"""//CREER_FENETRE_PRINCIPALE//
Crée la fenêtre principale de l'application.
@return root: Fenêtre principale
@return search_entry: Champ de recherche pour entrer le nom d'une station
@return suggestion_frame: Cadre pour afficher les suggestions
@return display_frame: Cadre pour afficher les résultats (départs)
@return train_widget: Liste mutable pour stocker les widgets de train
"""
def creer_fenetre_principale() -> tuple:
    # Configuration de l'apparence de l'interface
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title('Prochains départs')
    root.geometry('1600x900')
    root.resizable(False, False)

    # Chargement et définition de l'icône de la fenêtre
    im = Image.open("Icon/logo.png")
    photo = ImageTk.PhotoImage(im)
    root.wm_iconphoto(True, photo)

    # Création du cadre d'en-tête
    header_frame = ctk.CTkFrame(root, fg_color="white")
    header_frame.pack(fill=ctk.X)

    # Création et configuration de l'étiquette affichant l'heure
    time_label = ctk.CTkLabel(header_frame, text="--:--:--", font=("Arial", 30, "bold"), fg_color="#7B8E94", 
                              corner_radius=5, text_color="white")
    time_label.pack(side=ctk.LEFT, padx=10, pady=5)
    maj_heure(root, time_label)

    # Titre de l'interface
    title_label = ctk.CTkLabel(header_frame, text="Next Trains", font=("Arial", 25, "bold"), fg_color="white", 
                               text_color="#728387")
    title_label.pack(side=ctk.LEFT, padx=20)

    # Étiquette indiquant la voie
    voie_label = ctk.CTkLabel(header_frame, text="Voie", font=("Arial", 25, "bold"), fg_color="#0E1436", 
                              text_color="white", corner_radius=5)
    voie_label.pack(side=ctk.RIGHT, padx=10)

    # Champ de recherche pour entrer le nom d'une station
    search_entry = ctk.CTkEntry(header_frame, width=200, placeholder_text="Enter a station")
    search_entry.pack(side=ctk.RIGHT, padx=10)

    # Cadre pour afficher les résultats (départs)
    display_frame = ctk.CTkFrame(root, fg_color="#C0C0C0")
    display_frame.pack(fill=ctk.BOTH, expand=True)

    # Cadre des suggestions (initialement caché)
    suggestion_frame = ctk.CTkFrame(root, fg_color="white")
    suggestion_frame.place_forget()

    # Création d'une liste mutable pour stocker les widgets de train
    train_widget = []

    # Association de l'événement "KeyRelease" pour mettre à jour les suggestions en fonction du texte entré
    search_entry.bind("<KeyRelease>", lambda event: maj_suggestions(search_entry, suggestion_frame, display_frame, root, train_widget))

    return root, search_entry, suggestion_frame, display_frame, train_widget


"""//MAJ_HEURE//
Mise à jour de l'heure affichée dans l'interface toutes les secondes.
@param root: Fenêtre principale
@param time_label: Étiquette affichant l'heure
"""
def maj_heure(root: ctk.CTk, time_label: ctk.CTkLabel) -> None:
    # Vérifie que la fenêtre principale existe toujours
    if not root.winfo_exists():
        return
    # Récupère l'heure actuelle au format HH:MM:SS
    now = datetime.datetime.now().strftime("%H:%M:%S")
    # Met à jour le widget time_label avec l'heure actuelle
    time_label.configure(text=now)
    # Planifie l'exécution de cette fonction après 1000 millisecondes (1 seconde)
    root.after(1000, maj_heure, root, time_label)
