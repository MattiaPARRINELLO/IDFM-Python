"""//NETOYER_FENETRE
Cette fonction permet de nettoyer une fenêtre en supprimant tous les composants qui la composent.
@param fenetre: la fenêtre à nettoyer
"""
def nettoyer_fenetre(fenetre):
    for composant in fenetre.winfo_children():
        composant.destroy()
