from game_message import GameMessage, Vector, Ship


class Finder:
    def find_enemy_position(self, gamemessage: GameMessage) -> Vector:
        enemy_ships: list[Ship] = self.find_enemy_ships(gamemessage)
        # if len(enemy_ships) < 1:
        #     enemy_ships_ids = [shipId for shipId in gamemessage.shipsPositions.keys() if shipId != gamemessage.ships.get(gamemessage.currentTeamId)]
        #     return gamemessage.shipsPositions.get(enemy_ships_ids[0])
        try:
            alive_ships: list[Ship] = list(filter(lambda ship: ship.currentHealth > 0, enemy_ships))
            alive_ships.sort(key=lambda ship: ship.currentHealth)
            return alive_ships[0].worldPosition
        except:
            print("ERROR (Finder) Failed to find enemies!")
            return Vector(0, 0)

    def find_enemy_ships(self, gamemessage: GameMessage) -> list[Ship]:
        team_id = gamemessage.currentTeamId
        enemy_ships = list(filter(lambda ship: ship.teamId != team_id, gamemessage.ships.values()))
        return enemy_ships
