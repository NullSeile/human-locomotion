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

if False:
    screen = pygame.display.set_mode((1200, 600))

    texture = pygame.image.load(os.path.join(ASSETS_PATH, "imgs/floor.png"))

    radius = 1.5
    center = (2, radius)
    clock = pygame.time.Clock()

body_def = BodyDef(DEFAULT_BODY_PATH)

data: Dict[str, List[float]] = {k: [] for k in body_def.joints.keys()}
data1: List[float] = list()


def loop(population: List[PersonSimulation], floor: WorldObject, fps: int):

    p = population[0]
    if not p.dead:
        data1.append(rad2deg(p.person.parts["torso"].body.angle))
    # for joint_id, joint in p.person.joints.items():
    #     data[joint_id].append(rad2deg(joint.GetReactionTorque(1 / 30)))
    # data1[joint_id].append(rad2deg(joint.GetReactionTorque(30)))
    # data[joint_id].append(rad2deg(joint.angle))

    if False:
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

        draw_person(p.person, screen, center, radius)

        draw_textured(floor, texture, screen, center, radius)

        pygame.display.flip()
        pygame.display.update()

    # global clock
    # clock.tick(fps)


run_a_generation(
    body_def=body_def,
    genomes=[genome],
    fps=30,
    generation=0,
    draw_loop=loop,
    color_function=lambda i, n: (255, 255, 255, 255),
)

plt.title(f"Angle Torso")
plt.plot(data1)
plt.tight_layout()
plt.show()


# name = "Torque"

# plt.title(f"{name} Maluc")
# plt.plot(data["torso-thigh_f"])
# plt.tight_layout()
# plt.show()

# plt.title(f"{name} Genoll")
# plt.plot(data["thigh_f-leg_f"])
# plt.tight_layout()
# plt.show()

# plt.title(f"{name} Turmell")
# plt.plot(data["leg_f-foot_f"])
# plt.tight_layout()
# plt.show()
