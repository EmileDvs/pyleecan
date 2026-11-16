from ....Classes_new.output.output import Output
from deap import base, creator, tools


def delete_toolbox(self) -> None:
    """OptiGenAlgNsga2Deap method to delete DEAP toolbox
    Parameters
    ----------
    self : OptiGenAlgNsga2Deap
    """

    # Delete toolbox
    self.toolbox = None

    # Delete creator classes
    del creator.FitnessMin
    del creator.Individual
