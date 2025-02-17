import tkinter as tk
import customtkinter as ctk

"""//CREER_ETIQUETTE_LOGO
Fonction qui crée une étiquette contenant le logo de la ligne
@param cadre: le cadre dans lequel l'étiquette sera placée
@param photo_logo: l'image du logo
@return etiquette_logo: l'étiquette contenant le logo
"""
def creer_etiquette_logo(cadre, photo_logo: tk.PhotoImage):
    etiquette_logo = tk.Label(cadre, image=photo_logo, bg='#1a1d3b')
    etiquette_logo.image = photo_logo  # garder une référence à l'image
    etiquette_logo.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    return etiquette_logo


"""//CREER_ETIQUETTE_MISSION
Fonction qui crée une étiquette contenant la mission
@param cadre: le cadre dans lequel l'étiquette sera placée
@param mission: la mission
@return etiquette_mission: l'étiquette contenant la mission
"""
def creer_etiquette_mission(cadre, mission:str):
    etiquette_mission = ctk.CTkLabel(cadre, text=mission, text_color='#6c757d', font=('Arial', 16))
    etiquette_mission.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    return etiquette_mission


"""//CREER_ETIQUETTE_STATION
Fonction qui crée une étiquette contenant la station vers laquelle le train se dirige
@param cadre: le cadre dans lequel l'étiquette sera placée
@param direction: la direction
@return etiquette_station: l'étiquette contenant la station
"""
def creer_etiquette_station(cadre, direction:str):
    etiquette_station = ctk.CTkLabel(cadre, text=direction, text_color='white', font=('Arial', 20, 'bold'))
    etiquette_station.grid(row=0, column=2, padx=10, pady=5, sticky='w')
    return etiquette_station


"""//CREER_ETIQUETTE_TEMPS
Fonction qui crée une étiquette contenant le temps en station
@param cadre: le cadre dans lequel l'étiquette sera placée
@param temps_en_station: le temps en station
@return etiquette_temps: l'étiquette contenant le temps en station
"""
def creer_etiquette_temps(cadre, temps_en_station:str):
    etiquette_temps = ctk.CTkLabel(cadre, text=temps_en_station, text_color='#6c757d', font=('Arial', 16))
    etiquette_temps.grid(row=0, column=3, padx=10, pady=5, sticky='w')
    return etiquette_temps


"""//CRRER_ETIQUETTE_RESTANT
Fonction qui crée une étiquette contenant le temps avant l'arrivée
@param cadre: le cadre dans lequel l'étiquette sera placée
@param temps_avant_arrivee: le temps avant l'arrivée
@param en_direct: si le train est en direct
@return etiquette_restant: l'étiquette contenant le temps avant l'arrivée
"""
def creer_etiquette_restant(cadre, temps_avant_arrivee:str, en_direct:bool):
    couleur = "#28a745" if en_direct else "#dc3545"
    etiquette_restant = ctk.CTkLabel(cadre, text=temps_avant_arrivee, text_color=couleur,
                                     font=('Arial', 16, 'bold'), corner_radius=20,
                                     fg_color='#1a1d3b', padx=10, pady=5)
    etiquette_restant.grid(row=0, column=5, padx=10, pady=5, sticky='e')
    return etiquette_restant


"""//CREER_ETIQUETTE_VOIE
Fonction qui crée une étiquette contenant la voie
@param cadre: le cadre dans lequel l'étiquette sera placée
@param voie: la voie
@return etiquette_voie: l'étiquette contenant la voie
"""
def creer_etiquette_voie(cadre, voie:str):
    etiquette_voie = ctk.CTkLabel(cadre, text=voie, fg_color='white', text_color='black',
                                  font=('Arial', 18, 'bold'), width=50, height=50, corner_radius=25)
    etiquette_voie.grid(row=0, column=6, padx=10, pady=5, sticky='e')
    return etiquette_voie