"""//PRINTDEBUG//
Fonction qui permet d'afficher un message de debug
@param message : message à afficher
@return None
"""
def printDebug(message:str) -> None:
    print(f"DEBUG: {message}")


"""//AFFICHER_DEBUG_PASSAGE//
Fonction qui permet d'afficher les données d'un passage en mode debug
@param identifiantPassage : identifiant du passage
@param passageFormate : passage formaté
"""
def afficherDebugPassage(identifiantPassage:int, passageFormate:dict) -> None:
    printDebug("ID: " + str(identifiantPassage))
    printDebug("Direction: " + str(passageFormate["direction"]))
    printDebug("Misson : " + str(passageFormate["mission"]))
    printDebug("Arrive dans : " + str(passageFormate["arriveeDans"]))
    printDebug("Quai : " + str(passageFormate["quai"]))
    printDebug("Temps en station : " + str(passageFormate["tempsEnStation"]))
    printDebug("Ligne : " + str(passageFormate['ligne']["nom"]))
    printDebug("##############")