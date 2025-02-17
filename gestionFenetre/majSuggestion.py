from gestionDonnes.lectureFichiersJSON import avoir_stations
from gestionFenetre.gestionBouton import creer_bouton_suggestion
from gestionFenetre.nettoyageFenetre import nettoyer_fenetre


"""//MAJ_SUGGESTIONS
Fonction qui met à jour les suggestions de stations
@param search_entry: Champ de recherche
@param suggestion_frame: Cadre contenant les suggestions
@param display_frame: Cadre contenant les départs
@param root: Fenêtre principale
@param train_widget: Liste mutable contenant les widgets de train
"""
def maj_suggestions(search_entry, suggestion_frame, display_frame, root, train_widget):
    # Récupère les suggestions de stations (limitées à 5)
    suggestions = avoir_stations(search_entry.get(), limite=5)
    nettoyer_fenetre(suggestion_frame)
    
    if suggestions:
        # Affiche le cadre de suggestions au-dessous du champ de recherche
        suggestion_frame.place(x=search_entry.winfo_x(), y=search_entry.winfo_y() + search_entry.winfo_height())
        for suggestion in suggestions:
            creer_bouton_suggestion(suggestion, search_entry, suggestion_frame, display_frame, root, train_widget)
    else:
        # Si aucune suggestion n'est disponible, le cadre est masqué
        suggestion_frame.place_forget()


