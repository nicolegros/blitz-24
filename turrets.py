from game_message import GameMessage


class Turrets:
    def __init__(self):
        self.turrets = {}

    def load(self, gamemessage: GameMessage):
        myship = gamemessage.ships.get(gamemessage.currentTeamId)
        for turret in myship.stations.turrets:
            self.turrets[turret.id] = {
                "lockedIn": False if self.turrets.get(turret.id) is None else self.turrets.get(turret.id)["lockedIn"],
            }

    def lockin(self, turretid: str):
        self.turrets[turretid] = {
            "lockedIn": True
        }

    def isready(self, turretid: str) -> bool:
        try:
            ready = self.turrets[turretid]["lockedIn"]
        except:
            return False
        return ready

    def releaseall(self):
        self.turrets = {}