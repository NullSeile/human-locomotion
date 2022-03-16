import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import argparse

from simulation.genome import GenomeFactory
from simulation.simulation import Simulation
from utils import DEFAULT_BODY_PATH


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
        "--population",
        type=int,
        default=1024,
        help="Number of individuals in the population.",
    )
    parser.add_argument(
        "--n_processes",
        type=int,
        default=8,
        help="Number of processes to use for parallel simulation.",
    )
    # parser.add_argument(
    #     "--display",
    #     action="store_true",
    #     help="Whether or not display the simulation.",
    # )

    args = parser.parse_args()
    # width = 900
    # height = 600
    # screen = pygame.display.set_mode((width, height))

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
        # screen_to_draw=screen,
        parallel=True,
        population_size=args.population,
        n_processes=args.n_processes,
    )
    simulation.run()
