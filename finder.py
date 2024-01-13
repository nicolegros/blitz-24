from game_message import GameMessage, Vector, Ship


class Finder:
    def find_enemy_position(self, gamemessage: GameMessage) -> Vector:
        enemy_ships = self.find_enemy_ships(gamemessage)
        if len(enemy_ships) > 0:
            return enemy_ships[0].worldPosition
        else:
            return Vector(0, 0)

    def find_enemy_ships(self, gamemessage: GameMessage) -> list[Ship]:
        team_id = gamemessage.currentTeamId
        return list(filter(lambda ship: ship.teamId in [shipId for shipId in gamemessage.shipsPositions.keys() if shipId != team_id], gamemessage.ships.values()))
