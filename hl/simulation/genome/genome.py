from typing import Dict, List


class Genome:
    def __init__(self):
        pass

    def step(self, t: int) -> Dict[str, float]:
        pass


# What was first? the genome or the breeder?
class GenomeBreeder:
    def __init__(self, body_path: str):
        self.body_path = body_path

    def get_random_genome(self):
        raise NotImplementedError()

    def get_empty_genome(self):
        raise NotImplementedError()

    def get_genome_from_breed(
        self, parent_genomes: List[Genome], distr: List[float]
    ) -> Genome:
        raise NotImplementedError()
