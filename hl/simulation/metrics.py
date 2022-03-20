import numpy as np


def average_distance_person(person_simulation) -> float:
    return np.average(
        [
            person_simulation.person.parts[leg].body.position.x
            for leg in ["leg_f", "leg_b"]
        ]
    )
