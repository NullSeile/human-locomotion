import os
from typing import Optional

from hl.simulation.genome.sine_genome_symetric_v3 import SineGenomeBreeder

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import argparse
import time
import multiprocessing as mp

from hl.simulation.genome import get_genome_breeder, GENOME_CHOICES
from hl.simulation.simulation import Simulation
from hl.utils import ASSETS_PATH, DEFAULT_BODY_PATH, load_class_from_file

from hl.display.display import GUI_Controller


def check_thread_alive(thr):
    thr.join(timeout=0.0)
    return thr.is_alive()


def get_arguments():
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
    # parser.add_argument(
    #     "-g",
    #     "--genome",
    #     type=str,
    #     default="sine",
    #     choices=GENOME_CHOICES,
    #     help="The genome to use for the simulation.",
    # )
    parser.add_argument("--no_feet", "-nf", action="store_true")
    parser.add_argument(
        "--sample", "-sg", type=str, help="Choose a genome save to begin the training"
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_arguments()

    body_path = (
        os.path.join(ASSETS_PATH, "bodies/lil_man.json")
        if args.no_feet
        else DEFAULT_BODY_PATH
    )

    fps = 30
    # genome_breeder = get_genome_breeder(args.genome, args.bodypath)
    genome_breeder = SineGenomeBreeder(body_path)

    sample_genome = load_class_from_file(args.sample) if args.sample else None

    GUI_controller: Optional[GUI_Controller] = (
        GUI_Controller(genome_breeder.body_def, fps) if args.display else None
    )

    quit_flag = mp.Event()
    simulation = Simulation(
        genome_breeder,
        sample_genome=sample_genome,
        fps=fps,
        parallel=args.n_processes > 1 and not args.syncronous,
        population_size=args.population,
        n_processes=args.n_processes if not args.syncronous else 1,
        quit_flag=quit_flag,
    )
    if not args.syncronous:
        print("Starting simulation with async display")
        data_queue: mp.Queue = mp.Queue()
        simulation_process = mp.Process(target=simulation.run, args=(data_queue,))
        simulation_process.start()

        if args.display:
            assert isinstance(GUI_controller, GUI_Controller)
            GUI_controller.set_async_params(data_queue, quit_flag)
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
