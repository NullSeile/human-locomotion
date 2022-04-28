import numpy as np


def average_leg_x(person) -> float:
    return np.average(
        [person.person.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
    )
