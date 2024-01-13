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

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        self.actions = []
        self.turrets.load(game_message)

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if
                          crewmate.currentStation is None and crewmate.destination is None]
        turrets_to_go = []

        for crewmate in idle_crewmates:
            for stations_list in [
                crewmate.distanceFromStations.turrets,
                crewmate.distanceFromStations.radars,
                crewmate.distanceFromStations.shields,
                crewmate.distanceFromStations.helms
            ]:
                crew_stations = stations_list
                unoccupied_ship_stations = [station.id for station in my_ship.stations.turrets if
                                            station.operator is None and station.id not in turrets_to_go]
                l = list(filter(lambda turret: turret.stationId in unoccupied_ship_stations, crew_stations))
                if len(l) < 1:
                    pass
                else:
                    station_to_move_to = random.choice(l)
                    turrets_to_go.append(station_to_move_to.stationId)
                    self.addaction(CrewMoveAction(crewmate.id, station_to_move_to.stationPosition))

        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        myship = self.get_my_ship(game_message)
        # isdefense = myship.currentShield < 0.25 * game_message.constants.ship.maxShield
        isdefense = myship.currentShield < -1
        if isdefense:
            debrises, actualized_damaged = self.calculate_defense(game_message)

        for turret_station in operatedTurretStations:
            # Defense
            if isdefense and actualized_damaged:
                self.turrets.releaseall()
                debris_to_shoot = debrises[np.argmax(np.array(actualized_damaged))]
                position, _, _, _ = get_position_for_collision(game_message.constants.ship,
                                                                      debris_to_shoot.position.x,
                                                                      turret_station,
                                                                      debris_to_shoot)
            # Attack
            else:
                position = self.finder.find_enemy_position(game_message)

            print(f"POS: {position}")
            if self.turrets.isready(turret_station.id):
                self.addaction(TurretShootAction(turret_station.id))
            else:
                self.addaction(TurretLookAtAction(turret_station.id,
                                                  position))
                self.turrets.lockin(turret_station.id)

        # operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        # if operatedHelmStation:
        #     self.addaction(ShipRotateAction(random.uniform(0, 360)))

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
