from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING
from ....Classes_new.output.out_force import OutForce
from ....Classes_new.simulation.input_current import InputCurrent
from ..Input import InputError


if TYPE_CHECKING:
    from ....Classes_new.output.output import Output
    from ....Classes_new.simulation.simulation import Simulation


def gen_input(self, simu: Simulation | None = None, output: Output | None = None) -> None:
    """Generate the input for the structural module (skip force computation)

    Parameters
    ----------
    self : InputForce
        An InputForce object
    simu : Simulation, optional
        Simulation holding the input (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)
    """
    simu = container_or_parent(self, simu, "simu")
    output = container_or_parent(self, output, "output", depth=2)

    if output is None:
        raise InputError("The Simulation object must be in an Output object to run")

    if self.AGSF is None and self.AGSF_enforced is None:
        raise InputError("Input AGSF are missing")
    else:
        # generate OutElec from parent InputCurrent
        super(type(self), self).gen_input(simu=simu, output=output)

        # generate OutForce
        outforce = OutForce()

        if self.AGSF_enforced is not None:
            outforce.AGSF = self.AGSF_enforced
        else:
            if self.AGSF.name is None:
                self.AGSF.name = "Magnetic airgap surface force"
            if self.AGSF.symbol is None:
                self.AGSF.symbol = "AGSF"
            AGSF = self.AGSF.get_data()
            outforce.AGSF = AGSF

        # Update axes_dict
        outforce.axes_dict = dict()
        axes_list = outforce.AGSF.get_axes()
        for ax in axes_list:
            outforce.axes_dict[ax.name] = ax

        # Save the Output in the correct place
        output.force = outforce
