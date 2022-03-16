import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import argparse
import threading
import time

from simulation.genome import GenomeFactory
from simulation.simulation import Simulation
from hl.utils import DEFAULT_BODY_PATH
from hl.display.draw import draw_world

from hl.simulation.simulation import run_a_generation


def display_async(simulation: Simulation, screen: pygame.Surface):

    # world, floor = create_a_world()
    last_genomes, last_genomes_gen = simulation.obtain_last_genomes()
    if last_genomes is None:
        print("No genomes to display yet")
        return
    print("LEN GENOMES?", len(last_genomes))
    print("Displaying generation {}".format(last_genomes_gen))
    run_a_generation(
        simulation.genome_factory,
        last_genomes,
        simulation._fps,
        simulation.frames_per_step,
        False,
        screen,
    )
    # pygame.display.flip()


def check_thread_alive(thr):
    thr.join(timeout=0.0)
    return thr.is_alive()


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
        # screen_to_draw=screen,
        parallel=args.n_processes > 1,
        population_size=args.population,
        n_processes=args.n_processes,
    )

    population_lock = threading.Lock()
    simulation.add_population_lock(population_lock)
    simulation_thread = threading.Thread(target=simulation.run)
    simulation_thread.start()
    if args.display:
        while check_thread_alive(simulation_thread):
            display_async(simulation, screen)
            time.sleep(0.1)
    simulation_thread.join()
    print("Finished")
