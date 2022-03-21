from .array_genome import ArrayGenomeBreeder
from .sine_genome import SineGenomeBreeder
from .genome import GenomeBreeder


GENOME_CHOICES = ["sine", "s", "array", "a"]


def get_genome_breeder(
    genome_type: str, bodypath: str, loop_time: int = 30, actions_per_second: int = 1
) -> GenomeBreeder:
    """
    Returns a GenomeBreeder object for the given genome type.

    Parameters
    ----------
    genome_type : str
        The type of genome to use.
    bodypath : str
        The path to the body file to use.
    loop_time : int
        The number of seconds to loop the simulation for.
    actions_per_sec : int
        The number of actions to take per second.

    Returns
    -------
    GenomeBreeder
        The GenomeBreeder object to use.

    Raises
    ------
    ValueError
        If the genome type is not supported.
    """
    genome_params = {
        "body_path": bodypath,
    }

    if genome_type in ["sine", "s"]:
        return SineGenomeBreeder(**genome_params)
    elif genome_type in ["array", "a"]:
        genome_params["number_actions_loop"] = loop_time * actions_per_second
        genome_params["random_mutation_occurence"] = 0.5
        return ArrayGenomeBreeder(**genome_params)
    else:
        raise ValueError(
            f"Unknown genome type: '{genome_type}'. Select from: {GENOME_CHOICES}"
        )
