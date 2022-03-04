from typing import List
import pygame
from pygame.locals import QUIT
import sys
from Box2D import b2World, b2Vec2
import numpy as np
from tqdm import tqdm

from utils import RESORUCES_PATH, Color, hsv2rgb, map
from object import Object
from body_parser import parse_body

# from gym.envs.box2d.bipedal_walker


class Person:
    def __init__(
        self,
        world: b2World,
        actions: np.ndarray,
        frames_per_action: int,
        color: Color = (255, 255, 255, 255),
    ):
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
            if self.parts["head"].body.position.y < 0.9 or t >= self.max_frames:
                self.dead = True
                self.score = self.parts["torso"].body.position.x + t / self.max_frames
                return

            if t % self.frames_per_action == 0:
                for i, joint in enumerate(p.joints.values()):
                    joint.motorSpeed = p.actions[t // frames_per_action, i]

    def draw(self, screen: pygame.Surface, center: b2Vec2, radius: float):
        for p in self.parts.values():
            p.draw(screen, center, radius)


if __name__ == "__main__":

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    n_joints = 9
    actions_per_sec = 5
    max_time = 5
    actions_shape = (max_time * actions_per_sec, n_joints)

    fps = 30
    frames_per_action = fps // actions_per_sec

    population_size = 5

    for generation in range(5):

        print(f"Generation {generation}")

        world = b2World(gravity=(0, -9.8))

        people: List[Person] = list()
        for i in range(population_size):
            people.append(
                Person(
                    world,
                    np.random.rand(max_time * actions_per_sec, n_joints) * 2 - 1,
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
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((0, 0, 0))

            for p in people:
                p.update(t)

            world.Step(1 / fps, 2, 1)

            for p in people:
                p.draw(screen, (0, 2), 2)

            floor.draw(screen, (0, 2), 2)

            pygame.display.flip()
            pygame.display.update()

            clock.tick(fps) / 1000
            t += 1

            all_dead = True
            for p in people:
                if not p.dead:
                    all_dead = False

            if all_dead:
                break

        for p in people:
            print(p.score)
