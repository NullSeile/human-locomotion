# Global imports
from multiprocessing.pool import AsyncResult
from typing import Any, List, Optional, Tuple
from Box2D import b2World

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

import pygame
import numpy as np
from tqdm import tqdm
import threading
import multiprocessing as mp

# Our imports
from hl.simulation.genome import Genome, GenomeFactory
from hl.simulation.person import PersonSimulation
from hl.simulation.world_object import WorldObject

from hl.display.draw import draw_world
from hl.utils import ASSETS_PATH, DEFAULT_BODY_PATH, get_rgb_iris_index


def create_a_world() -> Tuple[b2World, WorldObject]:
    world = b2World(gravity=(0, -9.8))
    floor = WorldObject(
        [(-50, 0.1), (50, 0.1), (50, -0.1), (-50, -0.1)],
        world,
        (0, 0),
        0,
        dynamic=False,
    )
    return world, floor


def create_a_population(
    genome_factory: GenomeFactory, genomes: List[Genome], world: b2World
) -> List[PersonSimulation]:
    population: List[PersonSimulation] = []
    for i, genome in enumerate(genomes):
        person = PersonSimulation(
            genome_factory.body_path,
            genome,
            world,
            get_rgb_iris_index(i, len(genomes)),
        )
        population.append(person)

    return population


def run_a_generation(
    genome_factory: GenomeFactory,
    genomes: List[Genome],
    fps: int,
    frames_per_step: int,
    parallel: Optional[bool] = True,
    display_manager=None,
) -> List[float]:
    world, floor = create_a_world()
    population = create_a_population(genome_factory, genomes, world)

    t = 0
    while not all([p.dead for p in population]):
        # Step in the world
        world.Step(1 / fps, 2, 1)

        # If enough time has passed, update the population
        if t % frames_per_step == 0:
            for person in population:
                person.step()

        # Update metrics of population
        for person in population:
            person.update_status()

        # Draw the world
        if display_manager is not None and not parallel:
            display_manager.draw_world(population, floor)

        t += 1

    return [p.score for p in population]


import time


class SimulationQueuePutter(threading.Thread):
    def __init__(self, queue: mp.Queue, quit_flag: mp.Event):
        super().__init__()
        self.queue = queue
        self.quit_flag = quit_flag
        self.data = None

    def run(self):
        while not self.quit_flag.is_set():
            if self.data is not None:
                while not self.queue.empty():
                    self.queue.get()
                self.queue.put(self.data)
                self.data = None
            time.sleep(0.1)

    def add_last_genomes(
        self, generation: int, genomes: List[Genome], scores: List[float]
    ) -> None:
        self.data = (generation, genomes, scores)


class Simulation:
    def __init__(
        self,
        # Genome params
        genome_factory: GenomeFactory,
        # Simulation params
        fps: int = 30,
        frames_per_step: int = 5,
        population_size: int = 64,
        # Drawing
        # screen_to_draw: Optional[pygame.surface.Surface] = None,
        display_manager=None,
        # Parallel parameters
        parallel: bool = True,
        n_processes: int = 4,
        elite_genomes: int = 4,
        quit_flag: Optional[mp.Event] = None,
    ):
        self.genome_factory = genome_factory
        self.elite_genomes = elite_genomes

        self.parallel = parallel
        self.population_size = population_size
        self.n_processes = n_processes

        if self.parallel:
            if population_size % n_processes != 0:
                raise ValueError(
                    "In parallel simulation, the population_size must be divisible by"
                    " the number of processes."
                )

            if display_manager is not None:
                raise ValueError("Drawing is not supported yet in parallel simulation")

        # self.screen_to_draw = screen_to_draw
        self.display_manager = display_manager
        self.generation_count = -1

        self._fps = fps
        self.frames_per_step = frames_per_step
        # self.population_lock = population_lock
        # self.population_queue = population_queue
        # if self.parallel and self.population_lock is None:
        #     raise (
        #         ValueError("If parallel simulation is enabled, a lock must be provided")
        #     )
        self.population_queue_manager = None
        self._last_genomes = None
        self._last_genomes_generation = self.generation_count
        self.quit_flag = quit_flag

    def add_parallel_params(self, queue: mp.Queue) -> None:
        self.population_queue_manager = SimulationQueuePutter(queue, self.quit_flag)
        threading.Thread(target=self.population_queue_manager.run).start()

    def add_last_genomes(
        self, genomes: List[Genome], scores: List[float], skip_if_blocked=True
    ) -> None:
        """
        Add the last generation of genomes to the simulation. This
        method is thread-safe.
        """
        if self.population_queue_manager is not None:
            self.population_queue_manager.add_last_genomes(
                self.generation_count, genomes, scores
            )

    def _create_world(self) -> Tuple[b2World, WorldObject]:
        return create_a_world()

    def _create_initial_genomes(self) -> List[Genome]:
        genomes: List[Genome] = []
        for i in range(self.population_size):
            genomes.append(self.genome_factory.get_random_genome())
        return genomes

    def _create_population_from_genomes(
        self, genomes: List[Genome], world: b2World
    ) -> List[PersonSimulation]:
        population: List[PersonSimulation] = []
        for i, genome in enumerate(genomes):
            person = PersonSimulation(
                self.genome_factory.body_path,
                genome,
                world,
                get_rgb_iris_index(i, len(genomes)),
            )
            population.append(person)

        return population

    def _run_generation(self, genomes: List[Genome]) -> List[float]:
        return run_a_generation(
            self.genome_factory,
            genomes,
            self._fps,
            self.frames_per_step,
            self.parallel,
            self.display_manager,
        )

    def _run_generation_parallel(self, genomes: List[Genome]) -> List[float]:
        pool = mp.Pool(self.n_processes)
        returns: List[AsyncResult] = []

        population_per_process = self.population_size // self.n_processes

        for n in range(self.n_processes):
            sli = slice(
                population_per_process * n,
                population_per_process * (n + 1),
            )
            returns.append(
                pool.apply_async(
                    run_a_generation,
                    args=[
                        self.genome_factory,
                        genomes[sli],
                        self._fps,
                        self.parallel,
                        self.display_manager,
                    ],
                )
            )

        pool.close()
        pool.join()

        scores: List[float] = []
        for p in returns:
            scores += p.get()

        return scores

    def _breed(self, genomes: List[Genome], scores: List[float]) -> List[Genome]:
        """
        Breed the population.
        """
        print("Max score:" + str(max(scores)))
        distr: List[float] = list(np.array(scores) / sum(scores))

        # Selecting the best genomes to keep for the next generation
        gs = list(zip(genomes, scores))
        gs = sorted(gs, key=lambda x: x[1], reverse=True)
        elite_genomes = gs[: self.elite_genomes]

        new_genomes: List[Genome] = [e[0] for e in elite_genomes]

        # Select only best 40 genomes to breed
        s_gs = gs[:40]
        s_genomes = [e[0] for e in s_gs]
        s_distr = list(np.array([e[1] for e in s_gs]) / sum([e[1] for e in s_gs]))
        for _ in tqdm(
            range(self.population_size - self.elite_genomes), desc="Breeding  "
        ):
            genome = self.genome_factory.old_get_genome_from_breed(s_genomes, s_distr)
            new_genomes.append(genome)

        return new_genomes

    def obtain_some_genomes(self, n: int) -> List[Genome]:
        """
        Obtain some genomes from the population. It is thread-safe. First
        it locks the accesss to self.some_genomes, then obtains n genomes
        well distributed through the scores.
        """
        self._lock_genomes.acquire()
        if len(self.some_genomes) < n:
            self.some_genomes = self.genome_factory.get_random_genomes(n)
        self._lock_genomes.release()

        return self.some_genomes[:n]

    def has_converged(self, threshold: float = 0.01) -> bool:
        """
        Checks if the simulation has converged. This is done by checking if the
        average score of the last 10 generations is below a threshold.
        """
        return False
        # return (
        #     False
        #     if self.scores is None
        #     else sum(self.scores) / len(self.scores) < threshold
        # )

    def forced_quit(self) -> bool:
        if self.quit_flag is not None:
            return self.quit_flag.is_set()

    def run(
        self,
        data_queue: Optional[mp.Queue] = None,
    ) -> None:
        # Init parameters
        if data_queue is not None:
            self.add_parallel_params(data_queue)

        # Start the simulation
        genomes = self._create_initial_genomes()
        self.add_last_genomes(genomes, None)

        while not self.has_converged() and not self.forced_quit():
            self.generation_count += 1
            scores = (
                self._run_generation_parallel(genomes)
                if self.parallel
                else self._run_generation(genomes)
            )
            self.add_last_genomes(genomes, scores)
            if self.forced_quit():
                break
            genomes = self._breed(genomes, scores)
        if self.quit_flag is not None:
            self.quit_flag.set()
