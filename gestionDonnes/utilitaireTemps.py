import datetime

from autre.outilDebugage import printDebug


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