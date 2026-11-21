# Experimental pydantic model generated from Generator/ClassesRef/Simulation/Simu1.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from ...classes_common.errors import InputError
from ...classes_common.logger_context import get_logger
from ..electrical.electrical import Electrical
from ..force.force import Force
from ..loss.loss import Loss
from ..magnetics.magnetics import Magnetics
from ..structural.structural import Structural
from .simulation import Simulation


class Simu1(Simulation):
    """Five sequential weak coupling multi physics simulation

    Attributes
    ----------
    elec : Electrical or None
        Electrical module
        Default: None
    mag : Magnetics or None
        Magnetic module
        Default: None
    struct : Structural or None
        Structural module
        Default: None
    force : Force or None
        Force moduale
        Default: None
    loss : Loss or None
        Loss moduale
        Default: None
    """

    elec: Electrical | None = None
    """Electrical module"""
    mag: Magnetics | None = None
    """Magnetic module"""
    struct: Structural | None = None
    """Structural module"""
    force: Force | None = None
    """Force moduale"""
    loss: Loss | None = None
    """Loss moduale"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.Simu1.run_single
    def run_single(self) -> None:
        """Run the simulation

        Parameters
        ----------
        self : Simu1
            A Simu1 object

        """
        logger = get_logger(self)

        if self.parent is None:
            raise InputError("ERROR: Simulation object must be inside an Output object")
        output = self.parent
        output.geo = self.machine.comp_output_geo()

        # Init the input of the first module
        self.input.gen_input()

        # Run the modules
        if self.elec is not None:
            self.elec.run()
        if self.mag is not None:
            self.mag.run()

        if self.force is not None:
            self.force.run()
        # if self.HT is not None:
        #     self.HT.run()
        if self.struct is not None:
            self.struct.run()
        # if self.ac is not None:
        #     self.ac.run()

        if self.loss is not None:
            self.loss.run()
        # Running postprocessings

        if self.postproc_list:
            logger.info("Running simulation postprocessings...")
            for postproc in self.postproc_list:
                postproc.run(output)
