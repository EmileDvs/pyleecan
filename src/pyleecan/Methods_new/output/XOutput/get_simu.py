from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


def get_simu(self, index: int) -> Simulation:
    """
    Generate a simulation according to index

    Parameters
    ----------
    index: int
        simulation index

    Returns
    -------
    simu : Simulation
        simulation generated
    """

    # Get reference simulation
    ref_simu = self.simu

    # Construct the simulation
    simu = ref_simu.copy()
    simu.var_simu = None

    # Run setters
    for paramexplorer in self.paramexplorer_list:
        paramexplorer.setter(simu, paramexplorer.value[index])

    return simu
