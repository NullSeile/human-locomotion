import numpy as np


def max_distance_person(person):
    avg_leg_x = np.average(
        [person.person.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
    )
    score = max(0, avg_leg_x) + 1  # + 2 * t / person.max_frames

    return score**4
