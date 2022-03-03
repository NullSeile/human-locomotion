from utils import RESORUCES_PATH
import pygame
from pygame.locals import QUIT
import sys
from Box2D import b2World
import random

from object import Object
from body_parser import parse_body

if __name__ == "__main__":

    # world = b2World(gravity=(0, -9.8))
    world = b2World(gravity=(0, 0))

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    parts, joints = parse_body(RESORUCES_PATH + "bodies/body1.json", (0, 2), 0, world)

    parts["_floor"] = Object(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )

    fps = 30
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))

        for j in joints.values():
            j.motorSpeed = random.uniform(-1, 1)

        joints["torso-biceps_f"].motorSpeed = 1
        joints["torso-biceps_b"].motorSpeed = -1

        world.Step(1 / fps, 6, 3)

        for b in parts.values():
            b.draw(screen, (0, 2), 2)

        pygame.display.flip()
        pygame.display.update()

        clock.tick(fps) / 1000
