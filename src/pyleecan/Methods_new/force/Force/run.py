from ....classes_common.parents import container_or_parent
from ....classes_common.logger_context import get_logger
from ...simulation.Input import InputError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def run(self, output: Output | None = None) -> None:
    """Run the Force module

    Parameters
    ----------
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)
    """
    output = container_or_parent(self, output, "output", depth=2)
    if output is None and container_or_parent(self, None, "simu") is None:
        raise InputError(
            "ERROR: The Force object must be in a Simulation object to run"
        )
    if output is None:
        raise InputError("ERROR: The Force object must be in an Output object to run")

    get_logger(self).info("Starting Force module")

    # Compute and store time and angle axes from previous output
    # and returns additional axes in axes_dict
    axes_dict = self.comp_axes(output)

    # Compute the magnetic force according to the Force model
    out_dict = self.comp_force(output, axes_dict)

    # Store force quantities contained in out_dict in OutForce, as Data object if necessary
    output.force.store(out_dict, axes_dict)

    # Compute the air-gap surface force transfer if required
    if self.is_agsf_transfer:
        self.comp_AGSF_transfer(output, self.max_wavenumber_transfer)
