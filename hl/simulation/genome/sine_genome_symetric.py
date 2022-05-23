from enum import Enum, auto
from typing import Dict, List, Optional

import numpy as np

from hl.simulation.genome.genome import Genome, GenomeBreeder


class Joints(Enum):
    TORSO_HEAD = auto()

    TORSO_THIGH = auto()
    THIGH_LEG = auto()
    LEG_FOOT = auto()

    TORSO_BICEPS = auto()
    BICEPS_ARM = auto()


class SineGene:
    def __init__(self, amplitud: float, frequency: float, phase: float):
        self.amplitud = amplitud
        self.frequency = frequency
        self.phase = phase


class SineGenome(Genome):
    def __init__(self, genes: Dict[Joints, SineGene]):
        super().__init__()

        self.genes = genes

    def _func(self, gene: SineGene, t: int) -> float:
        return gene.amplitud * np.sin(t * gene.frequency + gene.phase)

    def step(self, t: int) -> Dict[str, float]:
        # This is bad, we need same frequ

        values: Dict[str, float] = dict()

        values["torso-head"] = self._func(self.genes[Joints.TORSO_HEAD], t)

        values["torso-thigh_f"] = self._func(self.genes[Joints.TORSO_THIGH], t)
        values["torso-thigh_b"] = -self._func(self.genes[Joints.TORSO_THIGH], t)

        values["thigh_f-leg_f"] = self._func(self.genes[Joints.THIGH_LEG], t)
        values["thigh_b-leg_b"] = -self._func(self.genes[Joints.THIGH_LEG], t)

        values["leg_f-foot_f"] = self._func(self.genes[Joints.LEG_FOOT], t)
        values["leg_b-foot_b"] = -self._func(self.genes[Joints.LEG_FOOT], t)

        values["torso-biceps_f"] = self._func(self.genes[Joints.TORSO_BICEPS], t)
        values["torso-biceps_b"] = -self._func(self.genes[Joints.TORSO_BICEPS], t)

        values["biceps_f-arm_f"] = self._func(self.genes[Joints.BICEPS_ARM], t)
        values["biceps_b-arm_b"] = -self._func(self.genes[Joints.BICEPS_ARM], t)

        return values


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
            genes[joint_id] = SineGene(0, 0, 0)

        return SineGenome(genes)

    def get_random_genome(self) -> SineGenome:
        genes = dict()
        for joint_id in Joints:
            amp = np.random.uniform(0, 1)
            freq = np.random.uniform(0, 1)
            phase = np.random.uniform(0, 6)
            genes[joint_id] = SineGene(amp, freq, phase)

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

            params = ["amplitud", "frequency", "phase"]

            genome.genes[joint_id] = SineGene(0, 0, 0)
            for p in params:
                val = getattr(parent_genome.genes[joint_id], p)

                if np.random.random() < mr:
                    val += np.random.normal(scale=self.mutation_scale)

                setattr(genome.genes[joint_id], p, val)

        return genome
