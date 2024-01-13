from typing import Optional

import numpy as np

from finder import Finder
from game_message import *
from actions import *
import random

from system_defense import will_meteor_hit, get_position_for_collision
from turrets import Turrets

LMBDA = 0.9


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.finder = Finder()
        self.turrets = Turrets()
        self.actions = []
        self.hasrotated = False
        self.crew_roles = {
            "helm": False,
            "turret": False,
            "radar": False,
            "shield": False
        }
        self.criticalshields = []

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """

        self.actions = []
        self.turrets.load(game_message)
        self.gamemessage = game_message
        self.turrets_to_go = []

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        shield_reparator_id = ""

        if self.isdefense(game_message) and not self.crew_roles["shield"]:
            print("Reparing shield!")
            shield_reparator = my_ship.crew[0]
            shield_reparator_id = shield_reparator.id
            shield = self.findshield(game_message)
            self.addaction(CrewMoveAction(shield_reparator.id, shield.gridPosition))
            self.turrets_to_go.append(shield.id)

        if self.iscritical(game_message):
            print("Damage critical: All to the shields!")
            for crewmate in my_ship.crew:
                if len(self.findshipshield(crewmate.currentStation)) < 1:
                    shield = self.findshield(game_message)
                    if shield is not None:
                        self.addaction(CrewMoveAction(crewmate.id, shield.gridPosition))
                        self.turrets_to_go.append(shield.id)
                        self.criticalshields.append(shield.id)

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if
                          crewmate.currentStation is None and crewmate.destination is None and crewmate.id != shield_reparator_id]

        for crewmate in idle_crewmates:
            # if game_message.tick > 1:
            if not self.crew_roles["radar"]:
                self.move_crew_to_type("radar", crewmate)
            if not self.crew_roles["helm"]:
                self.move_crew_to_type("helm", crewmate)
            # elif not self.crew_roles["shield"]:
            #     self.move_crew_to_type("shield", crewmate)
            else:
                self.move_crew_to_type("turret", crewmate)
        # else:
        #     self.move_crew_to_type("turret", crewmate)


        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]

        for turret_station in operatedTurretStations:
            position = self.finder.find_enemy_position(game_message)

            print(f"Shooting at: {position}")
            self.addaction(TurretLookAtAction(turret_station.id,
                                              position))
            self.addaction(TurretShootAction(turret_station.id))

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation and not self.hasrotated:
        if operatedHelmStation:
            myship = self.get_my_ship(game_message)
            enemy_position_to_attack = self.finder.find_enemy_position(game_message)
            print('-'*100)
            print(enemy_position_to_attack)
            found_turret = False
            for turret in operatedTurretStations:
                if turret.turretType is TurretType.Fast or turret.turretType is TurretType.Cannon or turret.turretType is TurretType.Sniper:
                    found_turret = True
                    turret_angle = turret.orientationDegrees
                    ship_position = myship.worldPosition
                    x_diff = enemy_position_to_attack.x - ship_position.x
                    y_diff = enemy_position_to_attack.y - ship_position.y

                    add_angle = 0
                    if x_diff < 0 and y_diff > 0 or x_diff < 0 and y_diff < 0:
                        add_angle = np.pi

                    angle_to_have_to_hit_enemy = np.arctan(y_diff/x_diff) * np.sign(y_diff / x_diff) + add_angle

                    angle_to_move = angle_to_have_to_hit_enemy - turret_angle
                    angle_to_move = angle_to_move / (2*np.pi)*360

                    add_addaction = ShipRotateAction(angle_to_move)

                    if turret.turretType is TurretType.Fast:
                        self.addaction(add_addaction)
                        print(f'angletomove: {angle_to_move}')
                        break

            if found_turret:
                self.addaction(add_addaction)


            self.hasrotated = True

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            self.addaction(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        # You can clearly do better than the random self.addaction( above! Have fun!
        return self.actions

    def addaction(self, action):
        print(f"Adding action: {action}")
        self.actions.append(action)

    def get_my_ship(self, gamemessage: GameMessage) -> Ship:
        team_id = gamemessage.currentTeamId
        return gamemessage.ships.get(team_id)

    def calculate_defense(self, game_message):
        myship = self.get_my_ship(game_message)
        actualized_damaged = []
        debrises = []
        for debris in game_message.debris:
            willhit, _, time = will_meteor_hit(myship.worldPosition,
                                               debris,
                                               game_message.constants.ship.stations.shield.shieldRadius)
            if willhit:
                debrises.append(debris)
                actualized_damaged.append(debris.damage * LMBDA ** time)

        return debrises, actualized_damaged

    def isdefense(self, gamemessage) -> bool:
        myship = self.get_my_ship(gamemessage)
        return myship.currentShield < 0.25 * gamemessage.constants.ship.maxShield
        # return myship.currentShield < -1

    def iscritical(self, gamemessage) -> bool:
        myship = self.get_my_ship(gamemessage)
        return myship.currentHealth < gamemessage.constants.ship.maxHealth * 0.20

    def findshield(self, gamemessage: GameMessage) -> Optional[Station]:
        myship = self.get_my_ship(gamemessage)
        try:
            selectedshield = list(filter(lambda shield: shield.id not in self.criticalshields, myship.stations.shields ))[0]
            return selectedshield
        except:
            print("No more shields")
            return None


    def getStationsOfType(self, stationType, gamemessage: GameMessage, crewmate: CrewMember) -> tuple[list[CrewDistance], list[Station]]:
        myship = self.get_my_ship(gamemessage)
        if stationType == "helm":
            return crewmate.distanceFromStations.helms, myship.stations.helms
        elif stationType == "turret":
            return crewmate.distanceFromStations.turrets, myship.stations.turrets
        elif stationType == "radar":
            return crewmate.distanceFromStations.radars, myship.stations.radars
        else:
            return crewmate.distanceFromStations.shields, myship.stations.shields

    def move_crew_to_type(self, stationtype: str, crewmate: CrewMember):
        crewmate_stations, ship_stations = self.getStationsOfType(stationtype, self.gamemessage, crewmate)
        print(f" Distances: {list(map(lambda station: station.distance, crewmate_stations))}")
        unoccupied_ship_stations = [station.id for station in ship_stations if
                                    station.operator is None and station.id not in self.turrets_to_go]
        l = list(filter(lambda turret: turret.stationId in unoccupied_ship_stations, crewmate_stations))
        if len(l) < 1:
            pass
        else:
            station_to_move_to = random.choice(l)
            self.turrets_to_go.append(station_to_move_to.stationId)
            self.addaction(CrewMoveAction(crewmate.id, station_to_move_to.stationPosition))
            self.crew_roles[stationtype] = True

    def findshipstation(self, stationid: str) -> Station:
        ship = self.get_my_ship(self.gamemessage)
        allstations = ship.stations.turrets + ship.stations.helms + ship.stations.radars + ship.stations.shields
        return list(filter(lambda station: station.id == stationid, allstations))[0]

    def findshipshield(self, stationid: str) -> list[Station]:
        ship = self.get_my_ship(self.gamemessage)
        return list(filter(lambda station: station.id == stationid, ship.stations.shields))
