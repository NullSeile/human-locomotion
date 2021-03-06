from abc import abstractmethod
from typing import Dict, List, Optional

from hl.io.body_def import BodyDef


class Genome:
    def __init__(self):
        pass

    def step(self, t: int) -> Dict[str, float]:
        pass


# What was first? the genome or the breeder?
class GenomeBreeder:
    def __init__(self, body_path: str):
        self.body_def = BodyDef(body_path)

    @abstractmethod
    def get_random_genome(self) -> Genome:
        raise NotImplementedError()

    @abstractmethod
    def get_empty_genome(self) -> Genome:
        raise NotImplementedError()

    @abstractmethod
    def get_genome_from_breed(
        self, parent_genomes: List[Genome], distr: List[float], mutation_rate: Optional[float] = None
    ) -> Genome:
        raise NotImplementedError()
