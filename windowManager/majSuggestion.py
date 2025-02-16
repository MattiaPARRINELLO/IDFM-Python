from lectureFichiersJSON import avoir_stations
from appelAPI import avoirProchainsDeparts
from traitementDonnee import formater_prochains_departs
from windowManager.createWidget import creer_widget
from windowManager.majTempsArrivee import maj_temps_arrivee

import customtkinter as ctk
import tkinter as tk


"""//MAJ_SUGGESTIONS//
Met à jour les suggestions de stations en fonction de la saisie de l'utilisateur.
@param search_entry: Champ de recherche dans lequel l'utilisateur saisit le nom de la station
@param suggestion_frame: Cadre dans lequel les suggestions sont affichées
@param display_frame: Cadre dans lequel les départs de train sont affichés
@param root: Fenêtre principale
@param train_widget: Liste mutable contenant les widgets de train
"""
def maj_suggestions(search_entry, suggestion_frame, display_frame, root, train_widget) -> None:
    # Récupère les suggestions de stations (limitées à 5)
    suggestions = avoir_stations(search_entry.get(), limite=5)
    # Supprime les widgets existants dans le cadre de suggestions
    for widget in suggestion_frame.winfo_children():
        widget.destroy()
    # Si des suggestions sont disponibles
    if suggestions:
        # Affiche le cadre de suggestions au-dessous du champ de recherche
        suggestion_frame.place(x=search_entry.winfo_x(), y=search_entry.winfo_y() + search_entry.winfo_height())
        # Pour chaque suggestion obtenue
        for suggestion in suggestions:
            # Définition des fonctions de rappel pour les événements de survol et de clic
            def on_enter(event):
                event.widget.configure(bg="#D3D3D3")
            def on_leave(event):
                event.widget.configure(bg="white")
            def on_click(label=suggestion['arrname']):
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
                search_entry.insert(0, label)
                suggestion_frame.place_forget()

                # Récupération du code de la station
                zdaid = avoir_stations(label)[0]['zdaid']
                # Suppression de tous les widgets affichés dans le cadre d'affichage
                for widget in display_frame.winfo_children():
                    widget.destroy()

                # Important : vider et mettre à jour la liste mutable train_widget
                train_widget.clear()
                prochainsDeparts = avoirProchainsDeparts(zdaid)
                prochainsDeparts = formater_prochains_departs(prochainsDeparts)
                # Création d'un widget pour chaque départ récupéré
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
            # Création du bouton de suggestion avec le nom de la station
            suggestion_button = ctk.CTkButton(suggestion_frame, text=suggestion['arrname'], 
                                              fg_color="white", text_color="black", anchor="w", 
                                              command=on_click)
            suggestion_button.pack(fill=ctk.X)
            # Liaison des événements de survol pour changer la couleur de fond
            suggestion_button.bind("<Enter>", on_enter)
            suggestion_button.bind("<Leave>", on_leave)
    else:
        # Si aucune suggestion n'est disponible, le cadre est masqué
        suggestion_frame.place_forget()


