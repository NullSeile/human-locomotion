import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import argparse
import threading
import time
import multiprocessing as mp
import numpy as np

from hl.simulation.genome import GenomeFactory
from hl.simulation.simulation import Simulation
from hl.utils import DEFAULT_BODY_PATH

# from hl.display.draw import draw_world
from hl.display.display import GUI_Controller

from hl.simulation.simulation import run_a_generation
import random


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
        default=mp.cpu_count(),
        help="Number of processes to use for parallel simulation.",
    )
    parser.add_argument(
        "-d",
        "--display",
        action="store_true",
        help="Whether or not display the simulation.",
    )
    parser.add_argument(
        "-s",
        "--syncronous",
        action="store_true",
        help=(
            "Whether or not run the program the simulation synchronously. If set to"
            " true, only one process will be used for the simulation, this includes the"
            " display. If '--display' is set, the display will be sent to the"
            " simulation"
        ),
    )

    args = parser.parse_args()

    GUI_controller = None
    if args.display:
        width = 900
        height = 600
        screen = pygame.display.set_mode((width, height))
        GUI_controller = GUI_Controller(screen)

    loop_time = 3
    actions_per_sec = 5
    genome_factory = GenomeFactory(
        bodypath=args.bodypath,
        number_actions_loop=loop_time * actions_per_sec,
    )
    quit_flag = mp.Event()
    simulation = Simulation(
        genome_factory,
        frames_per_step=actions_per_sec,
        fps=30,
        display_manager=GUI_controller if args.syncronous else None,
        parallel=args.n_processes > 1 and not args.syncronous,
        population_size=args.population,
        n_processes=args.n_processes if not args.syncronous else 1,
        quit_flag=quit_flag,
    )
    if not args.syncronous:
        print("Starting simulation with async display")
        data_queue = mp.Queue()
        simulation_process = mp.Process(target=simulation.run, args=(data_queue,))
        simulation_process.start()
        if args.display:
            GUI_controller.set_async_params(simulation, data_queue, quit_flag)
            while check_thread_alive(simulation_process) and not quit_flag.is_set():
                GUI_controller.display_async()
                time.sleep(0.1)
        if quit_flag.is_set():
            print("Exitting due key press")
        else:
            quit_flag.set()
        simulation_process.join()  # Wait for the simulation to finish before continuing

    else:
        simulation.run()
    print("Finished")
