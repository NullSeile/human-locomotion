# Public imports
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import os

# Private imports
from utils import Vec2, Color
from body_parser import get_joints_def, get_body_initial_pos
from utils import DEFAULT_BODY_PATH



class Genome:
    def __init__(
        self,
        pos: Vec2,
        actions_loop: pd.DataFrame,
        # angles: Dict[str, float],
        actions_first_step: Optional[pd.DataFrame] = None,
    ):
        self.pos = pos
        # self.angles = angles

        self.actions_loop = actions_loop
        self.actions_first_step = actions_first_step


def get_random_genome(
    body_path: str, number_actions_loop: int, number_actions_first_step: int
) -> Genome:
    # For now all angles are 0
    # random_angles = get_random_body_angles(body_path, 0.0)
    joints = get_joints_def(body_path)
    random_loop_actions = pd.DataFrame(
        data=np.random.rand(len(joints), number_actions_loop) * 2 - 1,
        index=joints.keys(),
    )
    genome = Genome(
        pos=get_body_initial_pos(body_path),
        # angles=random_angles,
        actions_loop=random_loop_actions,
    )
    return genome


def get_empty_genome(
    pos: Vec2, body_path: str, number_actions_loop: int, number_actions_first_step: int
) -> Genome:
    joints = get_joints_def(body_path)
    zeroes_loop_actions = pd.DataFrame(
        data=np.random.rand(len(joints), number_actions_loop) * 2 - 1,
        index=joints.keys(),
    )
    return Genome(
        pos=pos,
        actions_loop=zeroes_loop_actions,
    )


_MAX_FUSION_DEPTH = 5


# def recursive_fusion(
#     depth: int,
#     genome: Genome,
#     genome_parents: List[Genome],
#     distr: List[float],
#     min_idx: int,
#     max_idx: int,
# ) -> Genome:
#     """
#     Recursively merge two genomes by splitting the parameters into two parts
#     """
#     if depth == _MAX_FUSION_DEPTH:
#         return genome


class GenomeFactory:
    def __init__(
        self,
        bodypath: str = DEFAULT_BODY_PATH,
        number_actions_loop: int = 15,
        number_actions_first_step: int = 5,
    ):
        #  number_actions_first_step:int):
        self.body_path = bodypath
        self.number_actions_loop = number_actions_loop  # loop_time * actions_per_sec
        self.number_actions_first_step = number_actions_first_step
        self.initial_pos = get_body_initial_pos(self.body_path)
        self._joints = get_joints_def(bodypath)

    def get_random_genome(self):
        return get_random_genome(self.body_path, self.number_actions_loop, None)

    def get_empty_genome(self):
        return get_empty_genome(
            self.initial_pos, self.body_path, self.number_actions_loop, None
        )

    def get_genome_from_breed(
        self,
        parent_genomes: List[Genome],
        distr: List[float],
        max_idx_step_breeding: int = 4,
        min_idx_step_breeding: int = 2,
        random_mutation_occurence: float = 0.1,
    ) -> Genome:
        """
        Breed two genomes.

        It selects the parents and given its normalized distribution creates a child by
        crossing their genes using chunks of n-size.
        """
        if not len(parent_genomes) == len(distr):
            raise (
                ValueError(
                    "The number of parents and the distribution must be the same"
                )
            )
        # Creating the genome
        child = self.get_empty_genome()

        # Adding genes from parents
        gnome_index = 0
        while gnome_index < self.number_actions_loop:
            # Choose parents
            parent_genome: Genome = np.random.choice(parent_genomes, p=distr)

            # Choose the gene to add
            gene_idx = np.random.randint(min_idx_step_breeding, max_idx_step_breeding)
            gene_idx = min(gnome_index + gene_idx, self.number_actions_loop)

            # Add the gene
            child.actions_loop.iloc[
                :, gnome_index:gene_idx
            ] = parent_genome.actions_loop.iloc[:, gnome_index:gene_idx]
            gnome_index = gene_idx

        # Mutate the genome
        randarr = np.random.choice(
            [True, False],
            size=self.number_actions_loop * len(self._joints),
            p=[random_mutation_occurence, 1 - random_mutation_occurence],
        )
        randmat = np.reshape(randarr, (len(self._joints), self.number_actions_loop))
        child.actions_loop.iloc[randmat] = np.random.random(
            size=np.count_nonzero(randmat)
        )

        return child

    def old_get_genome_from_breed(
        self, parent_genomes: List[Genome], distr: List[float]
    ) -> Genome:

        if not len(parent_genomes) == len(distr):
            raise (
                ValueError(
                    "The number of parents and the distribution must be the same"
                )
            )
        # Creating the genome
        child = self.get_empty_genome()

        for t in range(self.number_actions_loop):
            parent_genome = np.random.choice(parent_genomes, p=distr)

            if np.random.rand() > 0.01:
                child.actions_loop.loc[:, t] = parent_genome.actions_loop.loc[:, t]
            else:
                child.actions_loop.loc[:, t]
        return child
