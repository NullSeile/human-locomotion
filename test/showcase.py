import sys
import os

from hl.display.draw import draw_object, draw_textured
from hl.utils import ASSETS_PATH, deg2rad

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame

from Box2D import b2World
from hl.simulation.world_object import WorldObject


world = b2World(gravity=(0, -9.8))

floor_texture = pygame.image.load(os.path.join(ASSETS_PATH, "imgs/floor.png"))
floor = WorldObject(
    [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
    world,
    (40, 0),
    0,
    dynamic=False,
)

dice_texture = pygame.image.load(os.path.join(ASSETS_PATH, "imgs/dice.png"))
l = 0.15
dice = WorldObject(
    [(-l, -l), (-l, l), (l, l), (l, -l)],
    world,
    pos=(-0.5, 3.5),
    angle=deg2rad(45),
    restitution=0.55,
)

w = 1
h = 0.05
o1 = WorldObject(
    [(-w, -h), (-w, h), (w, h), (w, -h)],
    world,
    pos=(-0.9, 2.8),
    angle=deg2rad(-30),
    dynamic=False,
)

o2 = WorldObject(
    [(-w, -h), (-w, h), (w, h), (w, -h)],
    world,
    pos=(0.9, 1.8),
    angle=deg2rad(30),
    dynamic=False,
)

screen = pygame.display.set_mode((1000, 600))
fps = 30

radius = 2
center = (0, radius)

start = False
while not start:
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key in [pygame.K_ESCAPE, pygame.K_q]
        ):
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            start = True


clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key in [pygame.K_ESCAPE, pygame.K_q]
        ):
            sys.exit()

    world.Step(1 / fps, 6 * 10, 3 * 10)

    screen.fill((0, 0, 0))

    draw_textured(floor, floor_texture, screen, center, radius)
    draw_textured(dice, dice_texture, screen, center, radius)
    draw_object(o1, screen, center, radius)
    draw_object(o2, screen, center, radius)

    pygame.display.flip()
    pygame.display.update()

    clock.tick(fps)
