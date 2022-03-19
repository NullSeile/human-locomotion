from typing import Dict
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from pygame.locals import QUIT, KEYDOWN, K_RETURN  # type: ignore
from Box2D import b2World
import sys

from hl.utils import DEFAULT_BODY_PATH
from hl.io.body_def import BodyDef
from hl.io.body_parser import parse_body
from hl.display.draw import draw_object

world = b2World()

walk0: Dict[str, float] = {
    "torso-head": 0,
    "torso-biceps_f": -15,
    "biceps_f-arm_f": 10,
    "torso-biceps_b": 10,
    "biceps_b-arm_b": 40,
    "torso-thigh_f": 30,
    "thigh_f-leg_f": -45,
    "torso-thigh_b": -5,
    "thigh_b-leg_b": -5,
}
root0 = -1

walk1: Dict[str, float] = {
    "torso-head": -3,
    "torso-biceps_f": -25,
    "biceps_f-arm_f": 10,
    "torso-biceps_b": 20,
    "biceps_b-arm_b": 20,
    "torso-thigh_f": 20,
    "thigh_f-leg_f": -10,
    "torso-thigh_b": -15,
    "thigh_b-leg_b": -10,
}
root1 = 0

walk2: Dict[str, float] = {
    "torso-head": -1,
    "torso-biceps_f": -35,
    "biceps_f-arm_f": 10,
    "torso-biceps_b": 33,
    "biceps_b-arm_b": 10,
    "torso-thigh_f": 33,
    "thigh_f-leg_f": -30,
    "torso-thigh_b": -25,
    "thigh_b-leg_b": -5,
}
root2 = -1

body_def = BodyDef(DEFAULT_BODY_PATH)
parts0, joints0 = parse_body(body_def, world, (251, 209, 121, 200), walk0, root0)
parts1, joints1 = parse_body(body_def, world, (251, 209, 121, 200), walk1, root1)
parts2, joints2 = parse_body(body_def, world, (251, 209, 121, 200), walk2, root2)

screen = pygame.display.set_mode((1100, 700))

screen.fill((255, 255, 255, 0))
# screen.fill("#C0C0C0")

for part in parts0.values():
    draw_object(part, screen, (1, 1), 1)

for part in parts1.values():
    draw_object(part, screen, (0, 1), 1)

for part in parts2.values():
    draw_object(part, screen, (-1, 1), 1)

pygame.display.flip()
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                print("nyee")
                pygame.image.save(screen, "screenshot.png")
