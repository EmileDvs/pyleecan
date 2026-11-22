# Experimental dataclass generated from Generator/ClassesRef/Simulation/Structural.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ...classes_common.errors import FieldMissingError, InputError
from ...classes_common.parents import container_or_parent
from .._legacy_class import LegacyClass
from ..output.out_struct import OutStruct

if TYPE_CHECKING:
    from ..output.output import Output


@dataclass(eq=False)
class Structural(LegacyClass):
    """Structural module abstract object

    Attributes
    ----------
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Structural"
    """

    logger_name: str = "Pyleecan.Structural"
    """Name of the logger to use"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.Structural.comp_axes
    def comp_axes(self, output: Output) -> None:
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

        if output.geo.axes_dict is None:
            raise FieldMissingError(
                "OutGeo.axes_dict is None: the geometry axes are not computed"
            )
        for key, val in output.geo.axes_dict.items():
            output.struct.axes_dict[key] = val

    # Inlined from Methods.Simulation.Structural.run
    def run(self, output: Output | None = None) -> None:
        """Run the Structural module

        Parameters
        ----------
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)
        """
        output = container_or_parent(self, output, "output", depth=2)
        if output is None and self.parent is None:
            raise InputError(
                "ERROR: The Structural object must be in a Simulation object to run"
            )
        if output is None:
            raise InputError(
                "ERROR: The Simulation object must be in an Output object to run"
            )

        self.comp_axes(output)

        group = self.force.group  # Magnetic force target

        # Init model, generate or import mechanical mesh
        self.init_mechanical_model(output, group)

        # Compute the magnetic force according to the Force model
        self.force.comp_force(output)
