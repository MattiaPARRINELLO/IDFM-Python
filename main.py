
#Ce script crée une interface graphique pour afficher les prochains départs de trains en utilisant la bibliothèque customtkinter (ctk).

from windowManager.creerFenetre import creer_fenetre_principale

train_widget = []


if __name__ == '__main__':
    # Création de la fenêtre principale et récupération des widgets clés
    root, search_entry, suggestion_frame, display_frame, train_widget = creer_fenetre_principale()
    # Démarrage de la boucle principale de l'interface graphique
    root.mainloop()
