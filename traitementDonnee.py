from debugtool import printDebug, afficherDebugPassage
from lectureFichiersJSON import avoir_information_ligne

import datetime

"""
Ce script contient les fonctions permettant de traiter les données reçues de l'API
"""

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

"""//OBTENIR_HEURE_ARRIVEE//
Fonction qui permet d'obtenir l'heure d'arrivée d'un passage
@param passage : passage à traiter
@return enDirect : booléen qui indique si l'heure d'arrivée est en direct
@return tmpArrivee : heure d'arrivée du passage
"""
def obtenir_heure_arrivee(passage: dict)->tuple:

    enDirect = True
    tmpArrivee = 0

    ### Définition des informations par défaut ###
    #Si le quai n'est pas trouvé, on le met à "#"
    if not passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ArrivalPlatformName"):
        passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"] = {"value": "#"}

    #Si l'heure d'arrivée est trouvée, on la met dans tmpArrivee
    if passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedArrivalTime"):
        tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
    
    else: #Sinon on cherche l'heure d'arrivée dans les autres champs
        if passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedArrivalTime"):
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedArrivalTime"]
        elif passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"):
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"]
        elif passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedDepartureTime"):
            tmpArrivee = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedDepartureTime"]
        else: #Si l'heure d'arrivée n'est pas trouvée, on passe au passage suivant
            printDebug("Aucune information sur l'heure d'arrivée")
            return False, None
        enDirect = False
    return enDirect, tmpArrivee

"""//EST_DESTINATION_ACTUELLE//
Fonction qui permet de vérifier si la destination du passage est la station actuelle
@param passage : passage à traiter
@return booléen qui indique si la destination est la station actuelle
"""
def est_destination_actuelle(passage: dict)->bool:
    if passage["MonitoredVehicleJourney"]["DestinationName"][0]["value"] == passage["MonitoredVehicleJourney"]["MonitoredCall"]["StopPointName"][0]["value"]:
        printDebug("---Saut du train---")
        printDebug("La destination est la station actuelle")
        printDebug("#####################")
        return True
    return False

"""//CALCULER_DIFFERENCE_TEMPS//
Fonction qui permet de calculer la différence de temps entre l'heure actuelle et l'heure d'arrivée
@param arriveeTMP : heure d'arrivée du passage
@return diff : différence de temps
@return diffMinutes : différence de temps en minutes
@return diffSecondes : différence de temps en secondes
"""
def calculerDifferenceTemps(arriveeTMP: str)->tuple:
    maintenant = datetime.datetime.now(datetime.timezone.utc).isoformat()
    diff = (datetime.datetime.fromisoformat(arriveeTMP) - datetime.datetime.fromisoformat(maintenant)).total_seconds()
    # Si le train est trop tôt ou trop tard ou si la différence est NaN
    if diff < -120 or diff > 3600 or diff != diff: #diff != diff pour vérifier si diff est NaN
        printDebug("---Saut du train---")
        printDebug("Le train est trop tôt ou trop tard")
        printDebug("#####################")
        return None, None, None 


    diffMinutes = int(diff / 60)
    diffSecondes = int(diff % 60)
    diff = f"{diffMinutes}m {diffSecondes}s"

    # Si le train est a quai
    if diffMinutes <= 0 and diffSecondes <= 0:
        diff = "🚉 ➡️" + diff

    return diff, diffMinutes, diffSecondes

"""//CALCULER_TEMPS_EN_STATION//
Fonction qui permet de calculer le temps en station
@param passage : passage à traiter
@param arriveeTMP : heure d'arrivée du passage
@return tempsEnStation : temps en station
"""
def calculer_temps_en_station(passage:dict, arriveeTMP:str)->str:
    # Si l'heure de départ en direct n'est pas trouvée alors on utilise l'heure de départ prévue
    if not passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"):
        passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"] = passage["MonitoredVehicleJourney"]["MonitoredCall"]["AimedDepartureTime"]

    #Crée une date à partir de l'heure de départ prévue
    depart = datetime.datetime.fromisoformat(passage["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedDepartureTime"])
    tempsEnStation = depart - datetime.datetime.fromisoformat(arriveeTMP)
    tempsEnStation = str(int(tempsEnStation.total_seconds())) + "s"

    if tempsEnStation == "0s" or tempsEnStation == "NaNs":
        tempsEnStation = None

    return tempsEnStation

"""//OBTENIR_MISSION//
Fonction qui permet d'obtenir la mission du passage
@param passage : passage à traiter
@return mission : mission du passage
"""
def obtenir_mission(passage:dict)->str:
    if len(passage["MonitoredVehicleJourney"]["JourneyNote"]) == 0:
        printDebug("Aucune mission trouvée")
        return ""
    return passage["MonitoredVehicleJourney"]["JourneyNote"][0]["value"]

"""//FORMATER_PASSAGE//
Fonction qui permet de formater un passage
@param passage : passage à traiter
@param identifiantPassage : identifiant du passage
@param enDirect : booléen qui indique si l'heure d'arrivée est en direct
@param arriveeTMP : heure d'arrivée du passage
@param diff : différence de temps
@param tempsEnStation : temps en station
@param misson : mission du passage
@return passageFormate : passage formaté
"""
def formaterPassage(passage:dict, identifiantPassage:int, enDirect:bool, arriveeTMP:str, diff:str, tempsEnStation:str, misson:str) -> dict:
    informationLigne = avoir_information_ligne(passage["MonitoredVehicleJourney"]["LineRef"]["value"])
    return {
        "id": identifiantPassage,
        "ligne": informationLigne,
        "direction": passage["MonitoredVehicleJourney"]["DestinationName"][0]["value"],
        "mission": misson,
        "aQuai": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("VehicleAtStop"),
        "arriveeEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedArrivalTime"),
        "arriveeEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedArrivalTime"),
        "departEnStationEXP": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ExpectedDepartureTime"),
        "departEnStationAIM": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("AimedDepartureTime"),
        "statut": passage["MonitoredVehicleJourney"]["MonitoredCall"].get("ArrivalStatus"),
        "quai": passage["MonitoredVehicleJourney"]["MonitoredCall"]["ArrivalPlatformName"]["value"],
        "longueur": passage["MonitoredVehicleJourney"]["VehicleFeatureRef"][0],
        "arriveeDans": diff,
        "arrivalTemp": arriveeTMP,
        "tempsEnStation": tempsEnStation,
        "enDirect": enDirect
    }

