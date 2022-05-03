from typing import Dict, List, Optional

import numpy as np

from hl.simulation.genome.genome import Genome, GenomeBreeder


class SineGene:
    def __init__(self, amplitud: float, frequency: float, phase: float, base: float):
        self.amplitud = amplitud
        self.frequency = frequency
        self.phase = phase
        self.base = base


class SineGenome(Genome):
    def __init__(self, genes: Dict[str, SineGene]):
        super().__init__()

        self.genes = genes

    def _func(self, gene: SineGene, t: int) -> float:
        return gene.amplitud * np.sin(t * gene.frequency + gene.phase)

    def step(self, t: int) -> Dict[str, float]:
        return {joint_id: self._func(gene, t) for joint_id, gene in self.genes.items()}


class SineGenomeBreeder(GenomeBreeder):
    def __init__(
        self,
        body_path: str,
        mutation_rate: float = 0.1,
        mutation_scale: float = 0.01,
    ):
        super().__init__(body_path)
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale

    def get_empty_genome(self) -> SineGenome:
        genes = dict()
        for joint_id in self.body_def.joints:
            genes[joint_id] = SineGene(0, 0, 0, 0)

        return SineGenome(genes)

    def get_random_genome(self) -> SineGenome:
        genes = dict()
        for joint_id in self.body_def.joints:
            amp = np.random.uniform(0, 1)
            freq = np.random.uniform(0, 1)
            phase = np.random.uniform(0, 6)
            base = np.random.uniform(-1.5, 1.5)
            genes[joint_id] = SineGene(amp, freq, phase, base)

        return SineGenome(genes)

    def get_genome_from_breed(
        self,
        parent_genomes: List[SineGenome],
        distr: List[float],
        mutation_rate: Optional[float] = None,
    ) -> SineGenome:

        mr = self.mutation_rate if mutation_rate is None else mutation_rate

        genome = self.get_random_genome()
        for joint_id in genome.genes:
            parent_genome: SineGenome = np.random.choice(parent_genomes, p=distr)

            params = ["amplitud", "frequency", "phase", "base"]

            genome.genes[joint_id] = SineGene(0, 0, 0, 0)
            for p in params:
                val = getattr(parent_genome.genes[joint_id], p)

                if np.random.random() < mr:
                    val += np.random.normal(scale=self.mutation_scale)

                setattr(genome.genes[joint_id], p, val)

        return genome
