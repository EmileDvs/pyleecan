# Experimental pydantic model generated from Generator/ClassesRef/Machine/MachineSync.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .machine import Machine


class MachineSync(Machine):
    """Abstract class for synchronous machine

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.MachineSync.comp_angle_rotor_initial
    def comp_angle_rotor_initial(self):
        """Compute rotor initial angle between rotor and stator d-axes
        Parameters
        ----------
        self : MachineSync
            A: MachineSync object
        Returns
        -------
        angle_rotor_initial: float
            rotor initial angle given by the difference of rotor and stator d-axes [rad]
        """

        return self.stator.comp_angle_d_axis() - self.rotor.comp_angle_d_axis()

    # Inlined from Methods.Machine.MachineSync.is_synchronous
    def is_synchronous(self):
        """Return if a machine is synchronous or not

        Parameters
        ----------
        self : MachineSync
            A MachineSync

        Returns
        -------
        is_synchronous: bool
            A MachineSync is synchronous

        """
        return True
