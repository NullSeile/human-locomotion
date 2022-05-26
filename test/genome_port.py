import argparse
import pickle
from typing import Dict

from hl.simulation.genome.sine_genome_symetric_v3 import (
    SineGenome as OGenome,
    JointType as OJoints,
    JointGene as OJointGene,
    JointGene as TJointGene,
)
from hl.simulation.genome.sine_genome_abdomen import (
    SineGenome as TGenome,
    JointType as TJoints,
    JointGene as TJointGene,
    SineGene as TSineGene,
)

from hl.utils import load_class_from_file

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
args = parser.parse_args()

# def joint_gene_port(o_joint_gene: OJointGene) -> TJointGene:
#     return []

original: OGenome = load_class_from_file(args.file)

genes: Dict[TJoints, TJointGene] = {
    TJoints.TORSO_HEAD: original.genes[OJoints.TORSO_HEAD],
    TJoints.TORSO_BICEPS: original.genes[OJoints.TORSO_BICEPS],
    TJoints.BICEPS_ARM: original.genes[OJoints.BICEPS_ARM],
    TJoints.TORSO_ABDOMEN: [TSineGene(0, 0)],
    TJoints.ABDOMEN_THIGH: original.genes[OJoints.TORSO_THIGH],
    TJoints.THIGH_LEG: original.genes[OJoints.THIGH_LEG],
    TJoints.LEG_FOOT: original.genes[OJoints.LEG_FOOT],
}

genome = TGenome(genes, original.frequency)

with open(
    "port.nye",
    "xb",
) as file:
    pickle.dump(genome, file)
