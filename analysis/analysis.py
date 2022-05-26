import argparse
import os
import sys
from typing import Dict, List
from matplotlib import pyplot as plt

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
import pygame
from hl.io.body_def import BodyDef
from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject
from hl.utils import ASSETS_PATH, DEFAULT_BODY_PATH, load_class_from_file, rad2deg
from hl.simulation.genome.sine_genome_symetric_v3 import SineGenome
from hl.simulation.simulation import run_a_generation
from hl.display.draw import draw_person, draw_textured

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

genome: SineGenome = load_class_from_file(args.file)

screen = pygame.display.set_mode((1200, 600))

texture = pygame.image.load(os.path.join(ASSETS_PATH, "imgs/floor.png"))

radius = 1.5
center = (2, radius)
clock = pygame.time.Clock()

body_def = BodyDef(DEFAULT_BODY_PATH)

angles: Dict[str, List[float]] = {k: [] for k in body_def.joints.keys()}


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

    p = population[0]
    for joint_id, joint in p.person.joints.items():
        angles[joint_id].append(rad2deg(joint.angle))

    draw_person(p.person, screen, center, radius)

    draw_textured(floor, texture, screen, center, radius)

    pygame.display.flip()
    pygame.display.update()

    # global clock
    # clock.tick(fps)


start = False
while not start:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            start = True

run_a_generation(
    body_def=body_def,
    genomes=[genome],
    fps=30,
    generation=0,
    draw_loop=loop,
    color_function=lambda i, n: (255, 255, 255, 255),
)

plt.plot(angles["torso-thigh_f"])
# plt.plot(angles["leg_b-foot_b"])
plt.show()
