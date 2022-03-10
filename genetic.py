from typing import List, Dict, Optional
import pygame
from pygame.locals import QUIT  # type: ignore

import sys
from Box2D import b2World
import numpy as np
import pandas as pd

from utils import RESORUCES_PATH, hsv2rgb, Vec2
from object import WorldObject
from body_parser import get_joints_def, get_random_body_angles
from person import MotionData, Person, BodyPartsDef
import os

# _i_hsv = 0
# _pop_size = 100


# def get_hsv2rgb_person():
#     global _i_hsv
#     global _pop_size
#     colour = hsv2rgb(_i_hsv / _pop_size, 0.5, 0.8, 0.5)
#     _i_hsv = (_i_hsv + 1) % _pop_size
#     return colour
def draw_world(screen, people, floor):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    for p in people:
        p.draw(screen, (2, 2), 2)

    floor.draw(screen, (2, 2), 2)

    pygame.display.flip()
    pygame.display.update()


def perform_generation(
    world: b2World,
    body_path: str,
    pos: Vec2,
    population_size: int,
    actions_list: List[MotionData],
    n_loops: int,
    # results: Optional[List[float]] = None,
    screen: Optional[pygame.surface.Surface] = None,
):
    # Create people
    people: List[Person] = list()
    for i in range(population_size):
        world.create_person()

        # body_parts = BodyPartsDef(
        #     body_path, pos, world, hsv2rgb(i / population_size, 0.5, 0.8, 0.5)
        # )
        # person = Person(
        #     body_parts,
        #     actions_list[i],
        #     n_loops,
        # )
        # people.append(person)

    t = 0
    clock = pygame.time.Clock()
    while not any([p.dead for p in people]):
        for p in people:
            p.update(t)

        world.Step(1 / fps, 2, 1)

        if screen is not None:
            draw_world(screen, people, floor)
        t += 1

    return [people[i].score for i in range(population_size)]


def evolve_generation(
    action_list: List[MotionData],
    scores: List[float],
) -> List[MotionData]:
    """
    Evolve the generation by selecting the best individuals and mutating the rest.

    Parameters
    ----------
    action_list : List[MotionData]
        List of all the actions in the generation.
    scores : List[float]
        List of all the scores in the generation.

    """
    population_size = len(actions_list)
    distr = np.array(scores) / sum(scores)

    new_actions_list = []
    for p in range(population_size):
        loop = pd.DataFrame(index=joints.keys())
        for t in range(loop_time * actions_per_sec):
            person_index = np.random.choice(range(len(action_list)), p=distr)
            if np.random.rand() > 0.01:
                loop.loc[:, t] = actions_list[person_index].loop.loc[:, t]
            else:
                loop.loc[:, t] = np.random.rand(len(joints)) * 2 - 1

        angles: Dict[str, float] = dict()
        for joint_id in joints:
            person_index = np.random.choice(range(population_size), p=distr)
            angles[joint_id] = actions_list[person_index].angles[joint_id]

        new_actions_list.append(MotionData(angles, loop, frames_per_action))

    return new_actions_list


if __name__ == "__main__":
    draw = False
    # Define world screen size
    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height)) if draw else None
    # Create world physics
    world = b2World(gravity=(0, -9.8))
    # Generate floor
    floor = WorldObject(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )

    # Obtain body model and defining its parameters
    body_path = os.path.join(RESORUCES_PATH, "bodies/body1.json")
    start_pos = (0, 1.31)
    actions_per_sec = 5
    loop_time = 3
    n_loops = 4

    fps = 30
    frames_per_action = fps // actions_per_sec

    # Defining simulation parameters
    population_size = 31

    joints = get_joints_def(body_path)
    actions_list: List[MotionData] = list()

    # Generate initial population actions
    for _ in range(population_size):
        # For now all angles are 0
        random_angles = get_random_body_angles(body_path, 0.0)
        random_loop_actions = pd.DataFrame(
            data=np.random.rand(len(joints), loop_time * actions_per_sec) * 2 - 1,
            index=joints.keys(),
        )
        random_body_motion = MotionData(
            angles=random_angles,
            loop=random_loop_actions,
            frames_per_action=frames_per_action,
        )
        actions_list.append(random_body_motion)

    generation = 0
    while True:
        # Perform generation
        print(f"Generation {generation}")
        scores = perform_generation(
            world,
            body_path,
            start_pos,
            population_size,
            actions_list,
            n_loops,
            screen,
        )

        # Print some stats
        print(f"{len(scores)}: avg={np.mean(scores):.4f}, max={max(scores):.4f}")

        actions_list = evolve_generation(actions_list, scores)

        generation += 1
