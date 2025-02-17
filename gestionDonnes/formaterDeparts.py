from autre.outilDebugage import printDebug, afficherDebugPassage
from gestionDonnes.utilitaireTemps import obtenir_heure_arrivee, calculerDifferenceTemps
from gestionDonnes.traitementDonnees import est_destination_actuelle, obtenir_mission, formaterPassage
from gestionDonnes.utilitaireTemps import calculer_temps_en_station


"""//FORMATER_PROCHAINS_DEPARTS//
Fonction principale qui permet de simplifier les données reçues de l'API
@param data : données reçues de l'API
@return dataRenvoyee : données formatées
"""
def formater_prochains_departs(data: dict)->list:
    dataRenvoyee = [] 
    dataPrincipale = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"] #Extraire les données principales
    identifiantPassage = 0 #Variable incrémentée pour chaque passage qui permet ainsi decréer un identifiant unique pour chaque passage
    #Début de la boucle pour simplifier les données de chaque passage
    for passage in dataPrincipale:
        printDebug("###---Nouveau passage---###")
        enDirect, tmpArrivee = obtenir_heure_arrivee(passage) #Obtenir l'heure d'arrivée du passage
        #Si l'heure d'arrivée n'est pas trouvée, on passe au passage suivant
        if not tmpArrivee:
            continue

        #Si la destination est la station actuelle, on passe au passage suivant
        if est_destination_actuelle(passage):
            continue

        #Calcul de la différence de temps entre l'heure actuelle et l'heure d'arrivée
        diff, _, _ = calculerDifferenceTemps(tmpArrivee)

        #Si la différence de temps n'est pas trouvée, on passe au passage suivant
        if diff is None:
            continue
        
        #Calcul du temps en station
        tempsEnStation = calculer_temps_en_station(passage, tmpArrivee)

        #Obtenir la mission du passage
        misson = obtenir_mission(passage)

        #Formate le passage a partir des donées obtenues et l'ajoute a la liste des passages
        passageFormate = formaterPassage(passage, identifiantPassage, enDirect, tmpArrivee, diff, tempsEnStation, misson)
        dataRenvoyee.append(passageFormate)

        #Affiche les données du passage en mode debug
        afficherDebugPassage(identifiantPassage, passageFormate)

        identifiantPassage += 1

    #Trie les passages par heure d'arrivée
    dataRenvoyee.sort(key=lambda x: x["arrivalTemp"])
    return dataRenvoyee