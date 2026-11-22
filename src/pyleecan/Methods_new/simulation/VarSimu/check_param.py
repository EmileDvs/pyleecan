from typing import TYPE_CHECKING
from ....classes_common.parents import container_or_parent


if TYPE_CHECKING:
    from ....Classes_new.simulation.simulation import Simulation


class VarSimuError(Exception):
    pass


def check_param(self, simu: Simulation | None = None) -> None:
    """Check VarParamSweep parameters validity

    Parameters
    ----------
    self : VarSimu
        A VarSimu object
    simu : Simulation, optional
        Simulation holding the object (default: the parent)
    """
    simu = container_or_parent(self, simu, "simu")
    # Local import: avoids circular imports
    from ....Classes_new.simulation.simulation import Simulation

    if type(self).__name__ == "VarSimu":
        raise VarSimuError(
            "VarSimu is an abstract class, please create one of its daughters."
        )

    # Check for simulation or VarSimu
    if simu is None or not isinstance(simu, Simulation):
        raise VarSimuError("VarSimu object must be inside a Simulation object")
