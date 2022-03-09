from typing import List, Dict
import pygame
from pygame.locals import QUIT  # type: ignore

import sys
from Box2D import b2World, b2Vec2
import numpy as np
from threading import Thread
import pandas as pd

from utils import RESORUCES_PATH, Color, hsv2rgb
from object import Object
from body_parser import get_joints_def, parse_body, get_random_body_angles


class PersonData:
    def __init__(self, angles: Dict[str, float], loop: pd.DataFrame):
        self.angles = angles
        self.loop = loop


class Person:
    def __init__(
        self,
        path: str,
        pos: b2Vec2,
        world: b2World,
        person_data: PersonData,
        frames_per_action: int,
        n_loops: int,
        color: Color = (255, 255, 255, 255),
    ):
        self.world = world
        self.parts, self.joints = parse_body(
            path, pos, 0, world, color, person_data.angles
        )

        self.loop = person_data.loop
        self.frames_per_action = frames_per_action
        self.frames_per_loop = len(self.loop) * frames_per_action
        self.n_loops = n_loops
        self.dead = False
        self.score = 0

    def update(self, t: int):
        if not self.dead:
            if self._is_dead() or t >= self.frames_per_loop * self.n_loops:
                self.dead = True
                self.score = self._calculate_score(t)

                for j in self.joints.values():
                    self.world.DestroyJoint(j)
                self.joints.clear()

                for p in self.parts.values():
                    self.world.DestroyBody(p.body)
                self.parts.clear()

                return

            if t % self.frames_per_action == 0:
                for joint_id, joint in self.joints.items():
                    loop_index = (t // frames_per_action) % len(self.loop)
                    joint.motorSpeed = self.loop[loop_index][joint_id]

    def draw(self, screen: pygame.Surface, center: b2Vec2, radius: float):
        for p in self.parts.values():
            p.draw(screen, center, radius)

    def _is_dead(self) -> bool:
        return self.parts["head"].body.position.y < 0.7

    def _calculate_score(self, t: float):
        avg_leg_x = np.average(
            [self.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
        )
        score = max(0, avg_leg_x) + 1  # + 2 * t / self.max_frames

        return score**4


def Generation(
    body_path: str,
    pos: b2Vec2,
    population_size: int,
    actions_list: List[pd.DataFrame],
    frames_per_action: int,
    n_loops: int,
    results=None,
    screen=None,
):

    world = b2World(gravity=(0, -9.8))

    people: List[Person] = list()
    for i in range(population_size):
        people.append(
            Person(
                body_path,
                pos,
                world,
                actions_list[i],
                frames_per_action,
                n_loops,
                hsv2rgb(i / population_size, 0.5, 0.8, 0.5),
            )
        )

    floor = Object(
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
    start_pos = b2Vec2(0, 1.31)

    actions_per_sec = 5
    loop_time = 3
    n_loops = 4

    fps = 30
    frames_per_action = fps // actions_per_sec

    n_threads = 1
    population_size = 31

    joints = get_joints_def(body_path)
    actions_list: List[PersonData] = list()
    for _ in range(population_size * n_threads):
        actions_list.append(
            PersonData(
                # For now all angles are 0
                angles=get_random_body_angles(body_path, 0.0),
                loop=pd.DataFrame(
                    data=np.random.rand(len(joints), loop_time * actions_per_sec) * 2
                    - 1,
                    index=joints.keys(),
                ),
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
                frames_per_action,
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

            new_actions_list.append(PersonData(angles, loop))

        actions_list = new_actions_list

        generation += 1
