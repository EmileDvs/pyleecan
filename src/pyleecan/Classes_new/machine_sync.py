# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineSync.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .machine import Machine


@dataclass(eq=False)
class MachineSync(Machine):
    """Abstract class for synchronous machine

    Attributes
    ----------
    """

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
