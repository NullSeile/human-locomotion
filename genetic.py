from typing import List
import pygame
from pygame.locals import QUIT
import sys
from Box2D import b2World, b2Vec2
import numpy as np
from threading import Thread

from utils import RESORUCES_PATH, Color, hsv2rgb
from object import Object
from body_parser import parse_body


class Person:
    def __init__(
        self,
        world: b2World,
        actions: np.ndarray,
        frames_per_action: int,
        color: Color = (255, 255, 255, 255),
    ):
        self.world = world
        # RESORUCES_PATH + "bodies/body1.json", b2Vec2(0, 1.31), 0, world, color
        # RESORUCES_PATH + "bodies/body_simple.json", b2Vec2(0, 0.69), 0, world, color
        self.parts, self.joints = parse_body(
            RESORUCES_PATH + "bodies/body1.json", b2Vec2(0, 1.31), 0, world, color
        )

        self.actions = actions
        self.frames_per_action = frames_per_action
        self.max_frames = len(actions) * frames_per_action
        self.dead = False
        self.score = 0

    def update(self, t: int):
        if not self.dead:
            if self._is_death() or t >= self.max_frames:
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
                for i, joint in enumerate(self.joints.values()):
                    joint.motorSpeed = self.actions[t // frames_per_action, i]

    def draw(self, screen: pygame.Surface, center: b2Vec2, radius: float):
        for p in self.parts.values():
            p.draw(screen, center, radius)

    def _is_death(self) -> bool:
        return self.parts["head"].body.position.y < 0.5

    def _calculate_score(self, t: float):
        avg_leg_x = np.average(
            [self.parts[leg].body.position.x for leg in ["leg_f", "leg_b"]]
        )
        score = max(0, avg_leg_x) + 0.1  # + 2 * t / self.max_frames

        return score**2


def Generation(
    population_size: int, actions_list: List[np.ndarray], results=None, screen=None
):

    world = b2World(gravity=(0, -9.8))

    people: List[Person] = list()
    for i in range(population_size):
        people.append(
            Person(
                world,
                actions_list[i],
                frames_per_action,
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

            clock.tick(fps)

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

    # n_joints = 4
    n_joints = 9
    actions_per_sec = 5
    max_time = 10
    actions_shape = (max_time * actions_per_sec, n_joints)

    fps = 30
    frames_per_action = fps // actions_per_sec

    n_threads = 10
    population_size = 70

    # n_threads = 2
    # population_size = 3

    actions_list = [
        np.random.rand(max_time * actions_per_sec, n_joints) * 2 - 1
        for _ in range(population_size * n_threads)
    ]

    generation = 0
    # for generation in range(1000):
    while True:

        print(f"Generation {generation}")

        threads: List[Thread] = list()
        scores_list = [[None] * population_size] * n_threads
        for n in range(n_threads):
            threads.append(
                Thread(
                    target=Generation,
                    args=(
                        population_size,
                        actions_list[n * population_size : (n + 1) * population_size],
                        scores_list[n],
                    ),
                )
            )
            threads[-1].start()

        for thread in threads:
            thread.join()

        scores = list()
        for n, s in enumerate(scores_list):
            scores += s

        distr = scores / sum(scores)

        print(f"{len(scores)}: avg={np.mean(scores):.4f}, max={max(scores):.4f}")

        if generation % 5 == 0:
            test_sample = 5
            best_index = np.argpartition(scores, -test_sample)[-test_sample:]
            print(best_index, [scores[i] for i in best_index])

            Generation(
                test_sample, [actions_list[i] for i in best_index], screen=screen
            )

        new_actions_list = list()

        for p in range(population_size * n_threads):
            actions = list()
            for t in range(actions_shape[0]):
                if np.random.rand() > 0.01:
                    actions.append(
                        actions_list[
                            np.random.choice(
                                range(population_size * n_threads), p=distr
                            )
                        ][t]
                    )
                else:
                    actions.append(np.random.rand(n_joints) * 2 - 1)

            new_actions_list.append(np.array(actions))

        actions_list = new_actions_list

        generation += 1
