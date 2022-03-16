import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import argparse

from simulation.genome import GenomeFactory
from simulation.simulation import Simulation
from hl.utils import DEFAULT_BODY_PATH
from hl.display.draw import draw_world


def display_async(simulation: Simulation, screen: pygame.Surface):
    while True:
        draw_world(simulation, screen)
        pygame.display.flip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genetic simulation for bipedal walkers."
    )
    parser.add_argument(
        "--bodypath",
        type=str,
        default=DEFAULT_BODY_PATH,
        help="Path to the body file.",
    )
    parser.add_argument(
        "-p",
        "--population",
        type=int,
        default=1024,
        help="Number of individuals in the population.",
    )
    parser.add_argument(
        "-j",
        "--n_processes",
        "--n_threads",
        type=int,
        default=8,
        help="Number of processes to use for parallel simulation.",
    )
    parser.add_argument(
        "-d",
        "--display",
        action="store_true",
        help="Whether or not display the simulation.",
    )

    args = parser.parse_args()

    screen = None
    if args.display:
        width = 900
        height = 600
        screen = pygame.display.set_mode((width, height))

    loop_time = 3
    actions_per_sec = 5
    genome_factory = GenomeFactory(
        bodypath=args.bodypath,
        number_actions_loop=loop_time * actions_per_sec,
    )
    simulation = Simulation(
        genome_factory,
        frames_per_step=actions_per_sec,
        fps=30,
        screen_to_draw=screen,
        parallel=args.n_processes > 1,
        population_size=args.population,
        n_processes=args.n_processes,
    )
    simulation.run()
