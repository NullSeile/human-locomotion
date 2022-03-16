from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from hl.simulation.genome.genome import Genome, GenomeBreeder
from hl.utils import DEFAULT_BODY_PATH


class ArrayGenome(Genome):
    def __init__(
        self,
        actions_loop: pd.DataFrame,
        actions_first_step: Optional[pd.DataFrame] = None,
    ):
        super().__init__()

        self.actions_loop = actions_loop
        self.actions_first_step = actions_first_step

    def step(self, t: int) -> Dict[str, float]:
        super().step(t)

        loop_index = t % len(self.actions_loop)
        return dict(self.actions_loop[loop_index])


class ArrayGenomeBreeder(GenomeBreeder):
    def __init__(
        self,
        body_path: str = DEFAULT_BODY_PATH,
        number_actions_loop: int = 15,
        number_actions_first_step: int = 5,
        min_idx_step_breeding: int = 2,
        max_idx_step_breeding: int = 4,
        random_mutation_occurence: float = 0.1,
    ):
        super().__init__(body_path)

        self.number_actions_loop = number_actions_loop  # loop_time * actions_per_sec
        self.number_actions_first_step = number_actions_first_step
        self.initial_pos = self.body_def.pos

        self.min_idx_step_breeding = min_idx_step_breeding
        self.max_idx_step_breeding = max_idx_step_breeding

        self.random_mutation_occurence = random_mutation_occurence

    def get_random_genome(self) -> ArrayGenome:
        # For now all angles are 0
        # random_angles = get_random_body_angles(body_path, 0.0)
        random_loop_actions = pd.DataFrame(
            data=np.random.rand(len(self.body_def.joints), self.number_actions_loop) * 2
            - 1,
            index=self.body_def.joints.keys(),
        )
        genome = ArrayGenome(
            actions_loop=random_loop_actions,
        )
        return genome

    def get_empty_genome(self) -> ArrayGenome:
        zeroes_loop_actions = pd.DataFrame(
            data=np.random.rand(len(self.body_def.joints), self.number_actions_loop) * 2
            - 1,
            index=self.body_def.joints.keys(),
        )
        return ArrayGenome(
            actions_loop=zeroes_loop_actions,
        )

    def get_genome_from_breed(
        self,
        parent_genomes: List[ArrayGenome],
        distr: List[float],
    ) -> ArrayGenome:
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
            gene_idx = np.random.randint(
                self.min_idx_step_breeding, self.max_idx_step_breeding
            )
            gene_idx = min(gnome_index + gene_idx, self.number_actions_loop)

            # Add the gene
            child.actions_loop.iloc[
                :, gnome_index:gene_idx
            ] = parent_genome.actions_loop.iloc[:, gnome_index:gene_idx]
            gnome_index = gene_idx

        # Mutate the genome
        randarr = np.random.choice(
            [True, False],
            size=self.number_actions_loop * len(self.body_def.joints),
            p=[self.random_mutation_occurence, 1 - self.random_mutation_occurence],
        )
        randmat = np.reshape(
            randarr, (len(self.body_def.joints), self.number_actions_loop)
        )
        child.actions_loop.iloc[randmat] = np.random.random(
            size=np.count_nonzero(randmat)
        )

        return child
