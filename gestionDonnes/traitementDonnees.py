from autre.outilDebugage import printDebug
from gestionDonnes.lectureFichiersJSON import avoir_information_ligne


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