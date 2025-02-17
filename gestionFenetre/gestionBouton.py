import customtkinter as ctk
import tkinter as tk

from gestionDonnes.lectureFichiersJSON import avoir_stations
from gestionDonnes.appelAPI import avoirProchainsDeparts
from gestionDonnes.formaterDeparts import formater_prochains_departs
from gestionFenetre.creerWidget import creer_widget
from gestionFenetre.majTempsArrivee import maj_temps_arrivee
from gestionFenetre.nettoyageFenetre import nettoyer_fenetre


"""//GERER_CLIQUE_BOUTON
Fonction qui gère le clic sur un bouton de suggestion
@param suggestion: Dictionnaire contenant les informations de la suggestion
@param search_entry: Champ de recherche
@param suggestion_frame: Cadre contenant les suggestions
@param display_frame: Cadre contenant les départs
@param root: Fenêtre principale
@param train_widget: Liste mutable contenant les widgets de train
"""
def gerer_clique_bouton(suggestion, search_entry, suggestion_frame, display_frame, root, train_widget):
    # Création d'une popup de chargement
    loading_screen = ctk.CTkToplevel(root)
    loading_screen.geometry("300x0")
    loading_screen.title("Chargement..")
    loading_label = ctk.CTkLabel(loading_screen, text="Chargement...", font=("Arial", 20, "bold"))
    loading_label.pack(expand=True)
    root.update()
    root.update_idletasks()

    # Mise à jour du champ de recherche avec la suggestion sélectionnée
    search_entry.delete(0, tk.END)
    search_entry.insert(0, suggestion['arrname'])
    suggestion_frame.place_forget()

    # Récupération du code de la station
    zdaid = avoir_stations(suggestion['arrname'])[0]['zdaid']
    nettoyer_fenetre(display_frame)
    train_widget.clear()

    # Récupération et affichage des prochains départs
    prochainsDeparts = avoirProchainsDeparts(zdaid)
    prochainsDeparts = formater_prochains_departs(prochainsDeparts)
    for depart in prochainsDeparts:
        creer_widget(
            display_frame, 
            depart['ligne']['image']['url'], 
            depart['mission'], 
            depart['direction'], 
            depart['enDirect'], 
            depart['tempsEnStation'], 
            depart['arriveeDans'], 
            depart['quai'], 
            depart["arrivalTemp"], 
            train_widget
        )
        
    loading_screen.destroy()
    # Mettre à jour les temps d'arrivée après 1 seconde
    root.after(1000, lambda: maj_temps_arrivee(train_widget, root))


"""//CREER_BOUTON_SUGGESTION
Crée un bouton de suggestion
@param suggestion: Dictionnaire contenant les informations de la suggestion
@param search_entry: Champ de recherche
@param suggestion_frame: Cadre contenant les suggestions
@param display_frame: Cadre contenant les départs
@param root: Fenêtre principale
@param train_widget: Liste mutable contenant les widgets de train
"""
def creer_bouton_suggestion(suggestion, search_entry, suggestion_frame, display_frame, root, train_widget):
    button = ctk.CTkButton(
        suggestion_frame, 
        text=suggestion['arrname'], 
        fg_color="white", 
        text_color="black", 
        anchor="w",
        command=lambda: gerer_clique_bouton(suggestion, search_entry, suggestion_frame, display_frame, root, train_widget)
    )
    button.pack(fill=ctk.X)