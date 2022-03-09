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

# _i_hsv = 0
# _pop_size = 100


# def get_hsv2rgb_person():
#     global _i_hsv
#     global _pop_size
#     colour = hsv2rgb(_i_hsv / _pop_size, 0.5, 0.8, 0.5)
#     _i_hsv = (_i_hsv + 1) % _pop_size
#     return colour


def Generation(
    body_path: str,
    pos: Vec2,
    population_size: int,
    actions_list: List[MotionData],
    n_loops: int,
    results: Optional[List[float]] = None,
    screen: Optional[pygame.surface.Surface] = None,
):

    world = b2World(gravity=(0, -9.8))

    people: List[Person] = list()
    for i in range(population_size):
        people.append(
            Person(
                BodyPartsDef(
                    body_path, pos, world, hsv2rgb(i / population_size, 0.5, 0.8, 0.5)
                ),
                actions_list[i],
                n_loops,
            )
        )

    floor = WorldObject(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )

    t = 0
    clock = pygame.time.Clock()
    while True:

        for p in people:
            p.update(t)

        world.Step(1 / fps, 2, 1)

        if screen is not None:

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

            # clock.tick(fps)

        t += 1

        all_dead = True
        for p in people:
            if not p.dead:
                all_dead = False

        if all_dead:
            break

    if results is not None:
        for i in range(population_size):
            results[i] = people[i].score


if __name__ == "__main__":

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    body_path = RESORUCES_PATH + "bodies/body1.json"
    start_pos = (0, 1.31)

    actions_per_sec = 5
    loop_time = 3
    n_loops = 4

    fps = 30
    frames_per_action = fps // actions_per_sec

    n_threads = 1
    population_size = 31

    joints = get_joints_def(body_path)
    actions_list: List[MotionData] = list()
    for _ in range(population_size * n_threads):
        actions_list.append(
            MotionData(
                # For now all angles are 0
                angles=get_random_body_angles(body_path, 0.0),
                loop=pd.DataFrame(
                    data=np.random.rand(len(joints), loop_time * actions_per_sec) * 2
                    - 1,
                    index=joints.keys(),
                ),
                frames_per_action=frames_per_action,
            )
        )

    generation = 0
    while True:

        print(f"Generation {generation}")

        # threads: List[Thread] = list()
        scores_list: List[List[float]] = [[0] * population_size] * n_threads
        for n in range(n_threads):

            Generation(
                body_path,
                start_pos,
                population_size,
                actions_list[n * population_size : (n + 1) * population_size],
                n_loops,
                scores_list[n],
                screen,
            )

            # threads.append(
            #     Thread(
            #         target=Generation,
            #         args=(
            #             population_size,
            #             actions_list[n * population_size : (n + 1) * population_size],
            #             scores_list[n],
            #         ),
            #     )
            # )
            # threads[-1].start()

        # for thread in threads:
        #     thread.join()

        scores: List[float] = list()
        for n, s in enumerate(scores_list):
            scores += s

        distr = np.array(scores) / sum(scores)

        print(f"{len(scores)}: avg={np.mean(scores):.4f}, max={max(scores):.4f}")

        # if generation % 5 == 0:
        #     test_sample = 5
        #     best_index = np.argpartition(scores, -test_sample)[-test_sample:]
        #     print(best_index, [scores[i] for i in best_index])

        #     Generation(
        #         test_sample, [actions_list[i] for i in best_index], screen=screen
        #     )

        new_actions_list = list()

        for p in range(population_size * n_threads):
            loop = pd.DataFrame(index=joints.keys())
            for t in range(loop_time * actions_per_sec):
                person_index = np.random.choice(
                    range(population_size * n_threads), p=distr
                )
                if np.random.rand() > 0.01:
                    loop.loc[:, t] = actions_list[person_index].loop.loc[:, t]
                else:
                    loop.loc[:, t] = np.random.rand(len(joints)) * 2 - 1

            angles: Dict[str, float] = dict()
            for joint_id in joints:
                person_index = np.random.choice(
                    range(population_size * n_threads), p=distr
                )
                angles[joint_id] = actions_list[person_index].angles[joint_id]

            new_actions_list.append(MotionData(angles, loop, frames_per_action))

        actions_list = new_actions_list

        generation += 1
