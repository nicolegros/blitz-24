import copy

import numpy as np

from game_message import Vector, Debris

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

        if add_time < 0:
            return None, debris

        if minus_time < 0:
            return add_time, debris
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








