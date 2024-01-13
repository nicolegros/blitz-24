import numpy as np
from game_message import *


class Near_station : 
    
    def __init__(self, game_message):
        self.game_message = game_message
        self.team_id = self.game_message.currentTeamId
        self.my_ship = self.game_message.ships.get(self.team_id)
        self.turrets_dict = self.fetch_turrets_dict()
        # self.distance_stations = self.f_go_near_stations()
        
    
    
    def fetch_turrets_dict(self):
        turret_dicts = {}
        for turret in self.my_ship.stations.turrets:
            if turret.turretType.value not in turret_dicts:
                turret_dicts[turret.turretType.value] = []
            turret_dicts[turret.turretType.value].append(turret.id)
        return turret_dicts
    
    def f_assign_turrets(self, actions, turrets_name : str = "NORMAL"):
        
            
        idle_crewmates = [crewmate for crewmate in self.my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        
        # Turret available
        operatedTurretStations = [station for station in self.my_ship.stations.turrets if station.operator is None]
    
        if len(idle_crewmates) > 0:
            crewmate_id = idle_crewmates[0]
            for station in crewmate_id.distanceFromStations.turrets :
                if station in operatedTurretStations:
                    station_id = station.id
                    if station_id in self.turret_dicts[turrets_name]:
                        station_to_move_to = station
   
                        print(f"crewmate going to turrets, {station_id}")
            # station_to_move_to = crewmate_id.distanceFromStations.turrets.Normal
                        return actions.append(CrewMoveAction(crewmate_id.id, station_to_move_to.stationPosition))
                   
        else:
            print("No crewmate available")
            return None
        # crew_closer_turrets = self.distance_stations["turrets_crew"][0]
        
        
        
    crew_test = Near_station(game_message)
    crew_test.f_assign_turrets(actions, "NORMAL")
        
        
    """
        
    def f_go_near_stations(self):
  
        other_ships_ids = [shipId for shipId in self.game_message.shipsPositions.keys() if shipId != self.team_id]
        
        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in self.my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]
        # Sort the crewmates based on distance to each station
        
        sorted_by_turrets = sorted(idle_crewmates, key=lambda x: list(map(lambda turret: turret.distance, x.distanceFromStations.turrets)))
        sorted_by_shields = sorted(idle_crewmates, key=lambda x: x.distanceFromStations.shields["distance"])
        sorted_by_radars = sorted(idle_crewmates, key=lambda x: x.distanceFromStations.radars["distance"])
        sorted_by_helms = sorted(idle_crewmates, key=lambda x: x.distanceFromStations.helms["distance"])
        print(sorted_by_turrets)
        
        distance_stations = {"turrets_crew" : sorted_by_turrets, 
                                "shields_crew" : sorted_by_shields, 
                                "radars_crew" :  sorted_by_radars,
                                "helm_crew" : sorted_by_helms}
            
        
        
        return distance_stations
        
        
    """


        
