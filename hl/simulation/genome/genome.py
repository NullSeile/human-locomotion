from typing import Dict, List

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

    def get_random_genome(self) -> Genome:
        raise NotImplementedError()

    def get_empty_genome(self) -> Genome:
        raise NotImplementedError()

    def get_genome_from_breed(
        self, parent_genomes: List[Genome], distr: List[float]
    ) -> Genome:
        raise NotImplementedError()
