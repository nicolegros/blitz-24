import numpy as np

def get_position_for_collision(self, x0: float, cannon: Cannon, meteor: Meteor, in_time: float = 0,
                               excess_trajectory=0):
    theta = np.pi - np.arctan(np.abs(meteor.velocity.y / meteor.velocity.x)) * np.sign(meteor.velocity.y)
    meteor_x = meteor.position.x + meteor.velocity.x * in_time + excess_trajectory * np.cos(theta)
    meteor_y = meteor.position.y + meteor.velocity.y * in_time + excess_trajectory * np.sin(theta)
    f_opt = lambda x: (cannon.position.x - meteor_x) * (
            meteor.velocity.y - self.constants.rockets.speed * np.sin(x)) - \
                      (cannon.position.y - meteor_y) * (
                              meteor.velocity.x - self.constants.rockets.speed * np.cos(x))

    root_0, _, ier, _ = fsolve(f_opt, np.array(x0), xtol=1e-9, full_output=True)
    t = (cannon.position.y - meteor.position.y) / (
            meteor.velocity.y - self.constants.rockets.speed * np.sin(root_0))

    min_idx = np.argmin(t, axis=0)
    angle = root_0[min_idx]
    t = t[min_idx]

    position = Vector(x=cannon.position.x + self.constants.rockets.speed * np.cos(angle) * t,
                      y=cannon.position.y + self.constants.rockets.speed * np.sin(angle) * t)
    return position, t, ier, angle / (2 * np.pi) * 360