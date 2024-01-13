import copy

import numpy as np
from scipy.optimize import fsolve
from game_message import Vector, Debris, TurretStation, ShipConstants



def will_meteor_hit(shipPosition: Vector, debris: Debris, shieldRadius):
    debris_y = debris.position.y
    debris_x = debris.position.x
    M = debris.velocity.y / debris.velocity.x
    k = debris_y - M*debris_x

    a = 1 - M**2
    b = 2*(M*(k-shipPosition.y) - shipPosition.x)
    c = shipPosition.x**2 + (k - shipPosition.y)**2 - shieldRadius**2

    interior_root = b ** 2 - 4 * a * c
    if interior_root < 0:
        return False, debris, None
    else:
        add_x = (-b + np.sqrt(interior_root)) / (2 * a)
        minus_x = (-b - np.sqrt(interior_root)) / (2 * a)

        t_add = (add_x - debris_x)/debris.velocity.x
        t_minus = (minus_x - debris_x) / debris.velocity.x

        if t_add < 0 and t_minus < 0:
            return False, debris, None
        else:
            if t_add < 0:
                return True, debris, t_minus
            elif t_minus < 0:
                return True, debris, t_add
            else:
                return True, debris, min(t_minus, t_add)

        # return True, debris, ((-b + np.sqrt(interior_root)) / (2 * a), (-b - np.sqrt(interior_root)) / (2 * a))

        # return True, debris,
        # add_time = (-b + np.sqrt(interior_root)) / (2 * a)
        # minus_time = (-b - np.sqrt(interior_root)) / (2 * a)
        #
        # if add_time < 0 and minus_time < 0:
        #     return False, debris
        #
        # if minus_time < 0:
        #     return True, debris
        #     # return add_time, debris
        #
        # if add_time < 0:
        #     return True, debris
        #     # return minus_time, debris
        #
        # else:
        #     return True, debris

def get_time_until_collision_from_center_of_debris(shipPosition: Vector, debris: Debris, shieldRadius):
    debris_y = debris.position.y - shipPosition.y
    debris_x = debris.position.x - shipPosition.x
    a = debris.velocity.y**2 + debris.velocity.x**2
    b = 2*(debris_y * debris.velocity.y + debris_x * debris.velocity.x)
    c = debris_y**2 + debris_x**2 - shieldRadius**2


    interior_root = b**2 - 4 * a * c
    if interior_root < 0:
        return None, debris
    else:
        add_time = (-b + np.sqrt(interior_root))/(2*a)
        minus_time = (-b - np.sqrt(interior_root))/(2*a)

        if add_time < 0 and minus_time < 0:
            return None, debris

        if minus_time < 0:
            return add_time, debris

        if add_time < 0:
            return minus_time, debris

        else:
            return min((-b + np.sqrt(interior_root))/(2*a), (-b - np.sqrt(interior_root))/(2*a)), debris

def get_othogonal_max_radius_position(debris: Debris):
    theta = np.pi - np.arctan(np.abs(debris.velocity.y / debris.velocity.x)) * np.sign(debris.velocity.y)
    theta = theta - np.pi/2

    x1 = debris.position.x + debris.radius * np.cos(theta)
    y1 = debris.position.y + debris.radius * np.sin(theta)

    x2 = debris.position.x - debris.radius * np.cos(theta)
    y2 = debris.position.y - debris.radius * np.sin(theta)

    debris1 = copy.copy(Debris)
    debris2 = copy.copy(Debris)

    debris1.velocity = Vector(x1, y1)
    debris2.velocity = Vector(x2, y2)

    return debris1, debris2

def get_position_for_collision(shipConstants:ShipConstants, x0: float, turret: TurretStation, debris: Debris, in_time: float = 0, excess_trajectory=0):
    rocket_speed = shipConstants.stations.turretInfos[turret.turretType].rocketSpeed
    theta = np.pi - np.arctan(np.abs(debris.velocity.y / debris.velocity.x)) * np.sign(debris.velocity.y)
    meteor_x = debris.position.x + debris.velocity.x * in_time + excess_trajectory * np.cos(theta)
    meteor_y = debris.position.y + debris.velocity.y * in_time + excess_trajectory * np.sin(theta)
    f_opt = lambda x: (turret.worldPosition.x - meteor_x) * (
            debris.velocity.y - rocket_speed * np.sin(x)) - \
                      (turret.worldPosition.y - meteor_y) * (
                              debris.velocity.x - rocket_speed * np.cos(x))

    root_0, _, ier, _ = fsolve(f_opt, np.array(x0), xtol=1e-9, full_output=True)
    t = (turret.worldPosition.y - debris.position.y) / (
            debris.velocity.y - rocket_speed * np.sin(root_0))

    min_idx = np.argmin(t, axis=0)
    angle = root_0[min_idx]
    t = t[min_idx]

    position = Vector(x=turret.worldPosition.x + rocket_speed * np.cos(angle) * t,
                      y=turret.worldPosition.y + rocket_speed * np.sin(angle) * t)
    return position, t, ier, angle/(2*np.pi)*360
def hit_meteor(debris:Debris, game_message, t, rate=1, in_time=0, excess_trajectory=0):
    next_move = []
    score = 0
    time_at_collision = 0
    explosion_meteors = []
    collision_position_meteor, time_to_collision_meteor, ier, angle = self.get_position_for_collision(0, game_message.cannon,
                                                                                         meteor, in_time, excess_trajectory)
    meteor_hit = False
    if self.position_is_in_map(collision_position_meteor) and ier == 1 and angle <88 and angle > -88:
        meteor_hit = True
        time_at_collision = t + time_to_collision_meteor
        next_move = [LookAtAction(target=collision_position_meteor), ShootAction()]
        score = self.constants.meteorInfos[meteor.meteorType].score * rate ** time_at_collision
        t += 10
        explosion_meteors = self.constants.meteorInfos[meteor.meteorType].explodesInto
        time_at_collision = copy.copy(time_at_collision)
    return meteor_hit, next_move, score, t, time_at_collision, explosion_meteors, collision_position_meteor








