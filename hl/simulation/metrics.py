import numpy as np


def average_leg_x(person) -> float:
    return np.average(
        [person.person.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
    )

def step_length(person) -> float:
    return abs(
        person.person.parts["leg_f"].body.position.x
        - person.person.parts["leg_b"].body.position.x
    )
