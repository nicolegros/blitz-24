import logging
import random

from game_message import GameMessage, Vector, Ship


class Finder:
    def __init__(self):
        self.logger = logging.getLogger("Finder")

    def find_enemy_position(self, gamemessage: GameMessage) -> Vector:
        enemy_ships: list[Vector] = self.find_enemy_ships_with_radar(gamemessage)
        if len(enemy_ships) < 1:
            enemy_ships = self.find_enemy_ships_without_radar(gamemessage)
            return enemy_ships[random.randrange(len(enemy_ships))]
        else:
            return enemy_ships[0]

    def find_enemy_ships_with_radar(self, gamemessage: GameMessage) -> list[Vector]:
        team_id = gamemessage.currentTeamId
        enemy_ships = list(filter(lambda ship: ship.teamId != team_id, gamemessage.ships.values()))
        try:
            alive_ships: list[Ship] = list(filter(lambda ship: ship.currentHealth > 0, enemy_ships))
            alive_ships.sort(key=lambda ship: ship.currentHealth)
            print(f"Alive ships health: {list(map(lambda ship: ship.currentHealth, alive_ships))}")
            return list(map(lambda ship: ship.worldPosition, alive_ships))
        except:
            self.logger.error("Failed to find enemies!")
            return []

    def find_enemy_ships_without_radar(self, gamemessage: GameMessage) -> list[Vector]:
        print("Finding ships without radar")
        ships = []
        my_ship_id = gamemessage.ships.get(gamemessage.currentTeamId)
        enemy_ships_ids = [shipId for shipId in gamemessage.shipsPositions.keys() if shipId != my_ship_id]
        for ship_id in enemy_ships_ids:
            if ship_id != my_ship_id:
                ships.append(gamemessage.shipsPositions.get(ship_id))

        return ships
