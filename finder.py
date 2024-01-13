from game_message import GameMessage, Vector, Ship


class Finder:
    def find_enemy_position(self, gamemessage: GameMessage) -> Vector:
        enemy_ships = self.find_enemy_ships(gamemessage)
        try:
            alive_ships = list(filter(lambda ship: ship.currentHealth > 0, enemy_ships))
            ship_with_minimal_health = alive_ships.sort(key=lambda ship: ship.currentHealth)[0]
            return ship_with_minimal_health
        except:
            return Vector(0, 0)

    def find_enemy_ships(self, gamemessage: GameMessage) -> list[Ship]:
        team_id = gamemessage.currentTeamId
        ships = list(filter(lambda ship: ship.teamId in [shipId for shipId in gamemessage.shipsPositions.keys() if
                                                     shipId != team_id], gamemessage.ships.values()))
        print(f"SHIPS: {list(map( lambda ship: {'id': ship.teamId, 'currentHealth': ship.currentHealth, 'position': ship.worldPosition}, ships))}")
        return ships
