# Experimental dataclass generated from Generator/ClassesRef/Simulation/InputForce.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .import_vector_field import ImportVectorField
from .input import Input
from .out_force import OutForce


@dataclass(eq=False)
class InputForce(Input):
    """Input to start with the structural one

    Attributes
    ----------
    P : ImportVectorField or None
        Magnetic air-gap surface force
        Unit: N.m^2; Default: None
    """

    P: ImportVectorField | None = None
    """Magnetic air-gap surface force"""

    # Inlined from Methods.Simulation.InputForce.gen_input
    def gen_input(self):
        """Generate the input for the structural module (skip force computation)

        Parameters
        ----------
        self : InputForce
            An InputForce object
        """

        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")

        if self.AGSF is None and self.AGSF_enforced is None:
            raise InputError("Input AGSF are missing")
        else:
            # generate OutElec from parent InputCurrent
            super(type(self), self).gen_input()

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
            self.parent.parent.force = outforce

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = InputForce.InputError
