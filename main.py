from gestionFenetre.creerFenetre import creer_fenetre_principale

if __name__ == '__main__':
    # Création de la fenêtre principale et récupération des widgets clés
    root, search_entry, suggestion_frame, display_frame, train_widget = creer_fenetre_principale()
    # Démarrage de la boucle principale de l'interface graphique
    root.mainloop()
