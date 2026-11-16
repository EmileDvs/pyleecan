from .check_param import VarSimuError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


def generate_simulation_list(self, ref_simu: Simulation | None = None) -> dict:
    """Generate all the simulation for the multi-simulation

    Parameters
    ----------
    self : VarSimu
        A VarSimu object
    ref_simu : Simulation
        Reference simulation to copy / update

    Returns
    -------
    multisim_dict : dict
        dictionary containing the simulation and paramexplorer list
    """
    raise VarSimuError(
        "VarSimu is an abstract class, please create one of its daughters."
    )
