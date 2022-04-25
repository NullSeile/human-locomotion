import os
import sys
import pickle
from typing import List

from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from hl.io.body_def import BodyDef

from hl.simulation.genome.sine_genome import SineGenome
from hl.simulation.simulation import run_a_generation
from hl.utils import DEFAULT_BODY_PATH
from hl.display.draw import draw_person, draw_object

path = input("Enter the genome file you want to watch: ")

genome: SineGenome = pickle.loads(open(path, "rb").read())

screen = pygame.display.set_mode((1200, 600))


def loop(population: List[PersonSimulation], floor: WorldObject):
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key in [pygame.K_ESCAPE, pygame.K_q]
        ):
            sys.exit()
            return

    screen.fill((0, 0, 0))

    for p in population:
        draw_person(p.person, screen, (2, 2), 2)

    draw_object(floor, screen, (2, 2), 2)

    pygame.display.flip()
    pygame.display.update()


run_a_generation(
    body_def=BodyDef(DEFAULT_BODY_PATH),
    genomes=[genome],
    fps=30,
    generation=0,
    draw_loop=loop,
)
