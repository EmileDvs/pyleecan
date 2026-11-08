# Experimental dataclass generated from Generator/ClassesRef/Simulation/Structural.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._error import InputError
from ._pyleecan_class import PyleecanClass
from .out_struct import OutStruct


@dataclass(eq=False)
class Structural(PyleecanClass):
    """Structural module abstract object

    Attributes
    ----------
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Structural"
    """

    logger_name: str = "Pyleecan.Structural"
    """Name of the logger to use"""

    # Inlined from Methods.Simulation.Structural.comp_axes
    def comp_axes(self, output):
        """Compute axes used for the Structural module

        Parameters
        ----------
        self : Structural
            a Structural object
        output : Output
            an Output object (to update)
        """
        if self.parent is None:
            raise InputError(
                "The Structural object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")

        # setup OutStruct if None
        if self.parent.parent.struct is None:
            self.parent.parent.struct = OutStruct()

        output.struct.axes_dict = {}

        for key, val in output.geo.axes_dict.items():
            output.struct.axes_dict[key] = val

    # Inlined from Methods.Simulation.Structural.run
    def run(self):
        """Run the Structural module"""
        if self.parent is None:
            raise InputError(
                "ERROR: The Structural object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError(
                "ERROR: The Simulation object must be in an Output object to run"
            )

        output = self.parent.parent

        self.comp_axes(output)

        group = self.force.group  # Magnetic force target

        # Init model, generate or import mechanical mesh
        self.init_mechanical_model(output, group)

        # Compute the magnetic force according to the Force model
        self.force.comp_force(output)
