import argparse
import os
import sys
import pickle
from typing import List

import numpy as np

from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from hl.io.body_def import BodyDef

from hl.simulation.genome.sine_genome import SineGenome, SineGenomeBreeder
from hl.simulation.simulation import run_a_generation
from hl.utils import DEFAULT_BODY_PATH, ASSETS_PATH
from hl.display.draw import draw_person, draw_object, draw_textured

parser = argparse.ArgumentParser()
parser.add_argument("--no_feet", "-nf", action="store_true")
parser.add_argument("files", nargs="+", type=str)
args = parser.parse_args()


body_path = (
    os.path.join(ASSETS_PATH, "bodies/lil_man.json")
    if args.no_feet
    else DEFAULT_BODY_PATH
)

genomes: List[SineGenome] = [
    pickle.loads(open(path, "rb").read()) for path in args.files
]

# body_path = DEFAULT_BODY_PATH
# genome_breeder = SineGenomeBreeder(body_path)
# genomes = [genome_breeder.get_random_genome() for _ in range(1)]

screen = pygame.display.set_mode((1200, 600))

texture = pygame.image.load(os.path.join(ASSETS_PATH, "imgs/floor.png"))

radius = 1.5
center = (2, radius)
clock = pygame.time.Clock()


def loop(population: List[PersonSimulation], floor: WorldObject, fps: int):
    for event in pygame.event.get():
        if (
            event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN
            and event.key in [pygame.K_ESCAPE, pygame.K_q]
        ):
            sys.exit()
            return

    global center

    people_x = [
        p.person.parts["torso"].body.position.x
        for p in population
        if "torso" in p.person.parts
    ]

    if people_x:
        cur_x = center[0]
        target_x = max(people_x)
        vel = (2 * (target_x - cur_x)) ** 3
        new_x = cur_x + vel * (1 / fps)
        center = (new_x, center[1])

    screen.fill((0, 0, 0))

    for p in population:
        draw_person(p.person, screen, center, radius)

    draw_textured(floor, texture, screen, center, radius)

    pygame.display.flip()
    pygame.display.update()

    global clock
    clock.tick(fps)


start = False
while not start:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            start = True

run_a_generation(
    body_def=BodyDef(body_path),
    genomes=genomes,
    fps=30,
    generation=0,
    draw_loop=loop,
    color_function=lambda i, n: (255, 255, 255, 255),
)
