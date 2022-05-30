from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

import numpy as np

from hl.simulation.genome.genome import Genome, GenomeBreeder


FOURIER_COUNT = 1
LIMITS: Dict[str, Tuple[float, float]] = {
    "amplitud": (-1, 1),
    "phase": (-3, 3),
    "frequency": (0, 0.2),
}


class JointType(Enum):
    TORSO_HEAD = auto()

    TORSO_BICEPS = auto()
    BICEPS_ARM = auto()

    TORSO_ABDOMEN = auto()

    ABDOMEN_THIGH = auto()
    THIGH_LEG = auto()
    LEG_FOOT = auto()


class SineGene:
    def __init__(self, amplitud: float, phase: float):
        self.amplitud = amplitud
        self.phase = phase


JointGene = List[SineGene]


class SineGenome(Genome):
    def __init__(self, genes: Dict[JointType, JointGene], frequency: float):
        super().__init__()

        self.genes = genes
        self.frequency = frequency

    def _func(self, joint_gene: JointGene, t: int) -> float:
        val = 0.0
        for i, gene in enumerate(joint_gene):
            val += (gene.amplitud / (i + 1)) * np.sin(
                (i + 1) * t * self.frequency + gene.phase
            )

        return val

    def step(self, t: int) -> Dict[str, float]:
        values: Dict[str, float] = dict()

        values["torso-head"] = self._func(self.genes[JointType.TORSO_HEAD], t)

        values["torso-abdomen"] = self._func(self.genes[JointType.TORSO_ABDOMEN], t)

        values["abdomen-thigh_f"] = self._func(self.genes[JointType.ABDOMEN_THIGH], t)
        values["abdomen-thigh_b"] = -self._func(self.genes[JointType.ABDOMEN_THIGH], t)

        values["thigh_f-leg_f"] = self._func(self.genes[JointType.THIGH_LEG], t)
        values["thigh_b-leg_b"] = -self._func(self.genes[JointType.THIGH_LEG], t)

        values["leg_f-foot_f"] = self._func(self.genes[JointType.LEG_FOOT], t)
        values["leg_b-foot_b"] = -self._func(self.genes[JointType.LEG_FOOT], t)

        values["torso-biceps_f"] = -self._func(self.genes[JointType.TORSO_BICEPS], t)
        values["torso-biceps_b"] = self._func(self.genes[JointType.TORSO_BICEPS], t)

        values["biceps_f-arm_f"] = -self._func(self.genes[JointType.BICEPS_ARM], t)
        values["biceps_b-arm_b"] = self._func(self.genes[JointType.BICEPS_ARM], t)

        return values


class SineGenomeBreeder(GenomeBreeder):
    def __init__(
        self,
        body_path: str,
        mutation_rate: float = 0.2,
        mutation_scale: float = 0.5,
    ):
        super().__init__(body_path)
        self.mutation_rate = mutation_rate
        self.mutation_scale = mutation_scale

    def get_empty_genome(self) -> SineGenome:
        genes: Dict[JointType, JointGene] = dict()
        for joint_id in self.body_def.joints:
            genes[joint_id] = [SineGene(0, 0)] * FOURIER_COUNT

        return SineGenome(genes, 0)

    def get_random_genome(self) -> SineGenome:
        genes: Dict[JointType, JointGene] = dict()
        for joint_id in JointType:
            genes[joint_id] = list()
            for _ in range(FOURIER_COUNT):
                amp = np.random.uniform(*LIMITS["amplitud"])
                phase = np.random.uniform(*LIMITS["phase"])
                genes[joint_id].append(SineGene(amp, phase))

        freq = np.random.uniform(*LIMITS["frequency"])

        return SineGenome(genes, freq)

    def _get_parent_genome(
        self, parent_genomes: List[SineGenome], distr: List[float]
    ) -> SineGenome:
        return np.random.choice(parent_genomes, p=distr)

    def _get_mutation(self, var_name: str) -> float:
        low, high = LIMITS[var_name]
        return np.random.normal(scale=self.mutation_scale * (high - low))

    def get_genome_from_breed(
        self,
        parent_genomes: List[SineGenome],
        distr: List[float],
        mutation_rate: Optional[float] = None,
    ) -> SineGenome:

        mr = self.mutation_rate if mutation_rate is None else mutation_rate

        genome = self.get_random_genome()
        for joint_id in genome.genes:

            joint_gene: JointGene = list()

            for i in range(FOURIER_COUNT):

                gene = SineGene(0, 0)

                parent_gene = self._get_parent_genome(
                    parent_genomes,
                    distr,
                ).genes[joint_id]

                for p in ["amplitud", "phase"]:
                    val = getattr(parent_gene[i], p)

                    if np.random.random() < mr:
                        val += self._get_mutation(p)

                    setattr(gene, p, val)

                joint_gene.append(gene)

            genome.genes[joint_id] = joint_gene

        val = self._get_parent_genome(parent_genomes, distr).frequency

        if np.random.random() < mr:
            val += self._get_mutation("frequency")

        genome.frequency = val

        return genome
