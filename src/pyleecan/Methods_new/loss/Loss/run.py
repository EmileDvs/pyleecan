from ....classes_common.parents import container_or_parent
from ....classes_common.logger_context import get_logger
from ...simulation.Input import InputError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def run(self, output: Output | None = None) -> None:
    """Run the Loss module

    Parameters
    ----------
    self : Loss
        A Loss model
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)
    """
    output = container_or_parent(self, output, "output", depth=2)
    if output is None and container_or_parent(self, None, "simu") is None:
        raise InputError("The Loss object must be in a Simulation object to run")
    if output is None:
        raise InputError("The Loss object must be in an Output object to run")

    get_logger(self).info("Running Loss module")

    # get output

    # Merge stator and rotor frame magnetic solutions once for all loss models
    meshsol = output.mag.get_meshsolution()

    axes_dict = self.comp_axes(output, meshsol=meshsol)
    # Comp and store in output
    self.comp_all_losses(axes_dict, meshsol=meshsol)
