# Experimental dataclass generated from Generator/ClassesRef/Simulation/Structural.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .out_struct import OutStruct
from .simulation import Simulation


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

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Simulation,)):
            raise TypeError(
                "Structural parent must be an instance of Simulation, or None; "
                + f"got {type(parent).__name__}"
            )

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

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = Structural.InputError
