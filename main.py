import pygame

from simulation import Simulation
from genome import GenomeFactory


if __name__ == "__main__":

    width = 900
    height = 600
    screen = pygame.display.set_mode((width, height))

    loop_time = 3
    actions_per_sec = 5
    genome_factory = GenomeFactory(
        number_actions_loop=loop_time * actions_per_sec,
    )
    simulation = Simulation(
        genome_factory,
        frames_per_step=actions_per_sec,
        fps=30,
        screen_to_draw=screen,
        syncronous_drawing=True,
    )
    simulation.run()
