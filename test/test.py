import os
import sys
import pickle
from Box2D import b2World

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from pygame import QUIT
from hl.io.body_def import BodyDef

from hl.simulation.genome.sine_genome import SineGenome
from hl.simulation.person import PersonSimulation
from hl.simulation.simulation import Simulation
from hl.simulation.world_object import WorldObject
from hl.utils import ASSETS_PATH, DEFAULT_BODY_PATH
from hl.display.draw import draw_person, draw_object

path = input("Enter the genome file you want to watch: ")

genome: SineGenome = pickle.loads(open(path, "rb").read())

world = b2World(gravity=(0, -9.8))
floor = WorldObject(
    [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
    world,
    (0, 0),
    0,
    dynamic=False,
)

person = PersonSimulation(
    BodyDef(DEFAULT_BODY_PATH), genome, world, (255, 255, 255, 255)
)

screen = pygame.display.set_mode((1200, 600))

fps = 30
frames_per_step = 5
t = 0
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    world.Step(1 / fps, 6 * 10, 3 * 10)

    if t % frames_per_step == 0:
        person.step()

    center = (2, 2)

    screen.fill((0, 0, 0))

    draw_person(person.person, screen, center, 2)
    draw_object(floor, screen, center, 2)

    t += 1

    pygame.display.flip()
    pygame.display.update()

    clock.tick(fps)
