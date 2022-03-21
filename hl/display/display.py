import pygame
from typing import Optional, List
import multiprocessing as mp
import numpy as np
import sys

from hl.simulation.simulation import run_a_generation
from hl.simulation.person import PersonSimulation
from hl.display.draw import draw_world


class GUI_Controller:
    def __init__(
        self,
        width=900,
        height=600,
    ):
        self.screen = pygame.display.set_mode((width, height))

        self.data_queue = None
        self.quit_flag = None
        self.simulation = None
        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS", 60)

        self.last_generation = None
        self.last_genomes = None
        self.last_scores = None

    def set_async_params(self, simulation, data_queue: mp.Queue, quit_flag: mp.Event):
        self.data_queue = data_queue
        self.quit_flag = quit_flag
        self.simulation = simulation
        # self.display_async(simulation)

    def draw_world(self, population: List[PersonSimulation], floor):
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key in [pygame.K_ESCAPE, pygame.K_q]
            ):
                pygame.quit()
                if self.quit_flag is not None:
                    self.quit_flag.set()
                sys.exit()
                return

        self.screen.fill((0, 0, 0))
        textsurface = self.font.render(
            f"Displaying Generation: {self.last_generation}", False, (255, 255, 255)
        )
        self.screen.blit(textsurface, (0, -2))

        draw_world(self.screen, population, floor)

        pygame.display.flip()
        pygame.display.update()

    def _refresh_last_data(self):
        if self.data_queue is None:
            raise (
                RuntimeError(
                    "First set params 'data_queue', 'quit_flag', and 'simulation' using"
                    " set_async_params"
                )
            )
        if not self.data_queue.empty():
            generation, last_genomes, last_scores = self.data_queue.get()
            self.last_generation = generation
            self.last_genomes = last_genomes
            self.last_scores = last_scores
        return (
            self.last_generation,
            self.last_genomes,
            self.last_scores,
        )

    def display_async(self):
        if self.data_queue is None:
            raise (
                RuntimeError(
                    "First set the data_queue and simulation using set_async_params"
                )
            )
        self._refresh_last_data()
        display_async(self, self.last_generation, self.last_genomes, self.last_scores)


def display_async(
    display: GUI_Controller,
    generation,
    last_genomes,
    last_scores,
):
    N_ELEMENTS = 16

    if last_genomes is None:
        return
    if last_scores is not None:
        gs = list(zip(last_genomes, last_scores))
        gs = sorted(gs, key=lambda x: x[1], reverse=True)
        idx = np.round(np.linspace(0, len(gs) - 1, N_ELEMENTS)).astype(int)
        selected_genomes = [gs[i][0] for i in idx]
    else:
        selected_genomes = last_genomes[:N_ELEMENTS]
    run_a_generation(
        display.simulation.genome_breeder,
        selected_genomes,
        display.simulation._fps,
        display.simulation.frames_per_step,
        False,
        display,
    )
