import numpy as np

import game_message
from game_message import *
from actions import *
import random

from system_defense import get_othogonal_max_radius_position, get_time_until_collision_from_center_of_debris, \
    get_position_for_collision, will_meteor_hit

LMBDA = 0.9

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")


    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """

        # actions = []
        # team_id = game_message.currentTeamId
        # my_ship = game_message.ships.get(team_id)
        # if len(game_message.debris):
        #     operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        #     debris = game_message.debris[0]
        #
        #     for turret_station in operatedTurretStations:
        #         where_to_shoot, _, _, _ = get_position_for_collision(game_message.constants.ship, debris.position.x,
        #                                                     turret_station, debris)
        #         print('position_to_shoot')
        #         print(where_to_shoot)
        #         actions += [
        #             # Charge the turret.
        #             # TurretChargeAction(turret_station.id),
        #             # Aim the turret itself.
        #
        #             TurretLookAtAction(turret_station.id,
        #                                where_to_shoot
        #                                ),
        #             # Shoot!
        #             TurretShootAction(turret_station.id)
        #         ]

            # get_position_for_collision(game_message.constants.ship, debris.position.x, game_message.)
            # for debris in game_message.debris:

                # print('debris_orthogonal')
                # print(get_othogonal_max_radius_position(debris))


                # t, _ = get_time_until_collision_from_center_of_debris(game_message.shipsPositions[game_message.currentTeamId], debris, game_message.constants.ship.stations.shield.shieldRadius)
                # if t is not None:
                #     print('time to hit')
                #     print(t)



        actions = []
        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id]

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [crewmate for crewmate in my_ship.crew if crewmate.currentStation is None and crewmate.destination is None]

        for crewmate in idle_crewmates:
            visitable_stations = crewmate.distanceFromStations.shields + crewmate.distanceFromStations.turrets + crewmate.distanceFromStations.helms + crewmate.distanceFromStations.radars
            station_to_move_to = random.choice(visitable_stations)
            actions.append(CrewMoveAction(crewmate.id, station_to_move_to.stationPosition))

        # Now crew members at stations should do something!
        operatedTurretStations = [station for station in my_ship.stations.turrets if station.operator is not None]
        for turret_station in operatedTurretStations:
            possible_actions = [
                # Charge the turret.
                TurretChargeAction(turret_station.id),
                # Aim the turret itself.
                TurretLookAtAction(turret_station.id,
                                   Vector(random.uniform(0, game_message.constants.world.width), random.uniform(0, game_message.constants.world.height))
                ),
                # Shoot!
                TurretShootAction(turret_station.id)
            ]

            actions.append(random.choice(possible_actions))

        operatedHelmStation = [station for station in my_ship.stations.helms if station.operator is not None]
        if operatedHelmStation:
            actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [station for station in my_ship.stations.radars if station.operator is not None]
        for radar_station in operatedRadarStation:
            actions.append(RadarScanAction(radar_station.id, random.choice(other_ships_ids)))

        # You can clearly do better than the random actions above! Have fun!


        # if game_message.tick > 100:
        #     actions = []
        #     team_id = game_message.currentTeamId
        #     my_ship = game_message.ships.get(team_id)
        #     if len(game_message.debris):
        #         operatedTurretStations = [station for station in my_ship.stations.turrets if
        #                                   station.operator is not None]
        #         debris_to_hit = []
        #         debris_dmg = []
        #         debris_time = []
        #         debris_actualized_damage = []
        #         for debris in game_message.debris:
        #
        #             # print(f'debris: {debris}')
        #             # t, _ = get_time_until_collision_from_center_of_debris(
        #             #     game_message.shipsPositions[game_message.currentTeamId], debris,
        #             #     game_message.constants.ship.stations.shield.shieldRadius)
        #             # print(t)
        #             # print(f'myposition: {my_ship.worldPosition}')
        #
        #             boo, debris_tmp, t = will_meteor_hit(
        #                 game_message.shipsPositions[game_message.currentTeamId], debris,
        #                 game_message.constants.ship.stations.shield.shieldRadius)
        #             print(f't: {t, boo}')
        #             # if t is not None:
        #             if boo:
        #                 debris_to_hit.append(debris_tmp)
        #                 debris_dmg.append(debris_tmp.damage)
        #                 debris_time.append(t)
        #                 debris_actualized_damage.append(debris_tmp.damage * LMBDA**t)
        #         if debris_actualized_damage:
        #             print(debris_actualized_damage)
        #             debris = debris_to_hit[np.argmax(np.array(debris_actualized_damage))]
        #
        #
        #             for turret_station in operatedTurretStations:
        #                 # if turret_station.charge<0:
        #                 #     turret_station.
        #                 where_to_shoot, _, _, _ = get_position_for_collision(game_message.constants.ship, debris.position.x,
        #                                                                      turret_station, debris)
        #                 print('position_to_shoot')
        #                 print(where_to_shoot)
        #                 actions += [
        #                     # Charge the turret.
        #                     # TurretChargeAction(turret_station.id),
        #                     # Aim the turret itself.
        #
        #                     TurretLookAtAction(turret_station.id,
        #                                        where_to_shoot
        #                                        ),
        #                     # Shoot!
        #                     TurretShootAction(turret_station.id)
        #                 ]



        return actions
