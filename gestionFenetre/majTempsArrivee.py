from autre.outilDebugage import printDebug
import datetime


"""//MAJ_TEMPS_ARRIVEE//
Met à jour les temps d'arrivée des trains en fonction de l'heure actuelle.
@param train_widget: Liste mutable contenant les widgets de train
@param root: Fenêtre principale
"""
def maj_temps_arrivee(train_widget, root):
    printDebug("Mise à jour des temps d'arrivée")
    maintenant = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # Itération sur une copie de train_widget pour permettre la suppression en toute sécurité
    for widget in train_widget.copy():
        # Calcul de la différence en secondes entre le temps d'arrivée prévu et l'heure actuelle
        diff = (datetime.datetime.fromisoformat(widget[2]) - 
                datetime.datetime.fromisoformat(maintenant)).total_seconds()
        # Suppression des widgets si la différence est trop négative ou trop grande ou si diff n'est pas un nombre
        if diff < -120 or diff > 3600 or diff != diff:  # Vérification NaN: diff != diff
            widget[0].destroy()
            train_widget.remove(widget)
            continue
        
        # Si le train est déjà arrivé ou dans l'instant précis
        if diff <= 0:
            diff = abs(diff)
            # Vérification si le retard dépasse une certaine marge (temps d'attente + 10 secondes)
            if diff > int(widget[3]) + 10: 
                widget[0].destroy()
                train_widget.remove(widget)
                continue
            diff = int(diff)
            diff = "🚉 ➡️" + str(diff)
        else:
            # Calcul du temps restant en minutes et secondes
            diffMinutes = int(diff / 60)
            diffSecondes = int(diff % 60)
            diff = f"{diffMinutes}m {diffSecondes}s"

        # Mise à jour de l'étiquette affichant le temps restant
        widget[1].configure(text=diff)

    # Planifie l'exécution récursive pour continuer les mises à jour toutes les secondes
    root.after(1000, lambda: maj_temps_arrivee(train_widget, root))
