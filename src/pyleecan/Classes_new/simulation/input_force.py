# Experimental dataclass generated from Generator/ClassesRef/Simulation/InputForce.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from ...classes_common.errors import InputError
from ...classes_common.parents import container_or_parent
from ..import_data.import_vector_field import ImportVectorField
from ..output.out_force import OutForce
from .input import Input

if TYPE_CHECKING:
    from ..output.output import Output
    from .simulation import Simulation


@dataclass(eq=False)
class InputForce(Input):
    """Input to start with the structural one

    Attributes
    ----------
    P : ImportVectorField or None
        Magnetic air-gap surface force
        Unit: N.m^2; Default: None
    """

    P: ImportVectorField | None = field(
        default=None, metadata={"unit": "N.m^2", "default_class": "ImportVectorField"}
    )
    """Magnetic air-gap surface force"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.InputForce.gen_input
    def gen_input(
        self, simu: Simulation | None = None, output: Output | None = None
    ) -> None:
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
            outforce.axes_dict = {}
            axes_list = outforce.AGSF.get_axes()
            for ax in axes_list:
                outforce.axes_dict[ax.name] = ax

            # Save the Output in the correct place
            output.force = outforce
