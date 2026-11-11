# Experimental dataclass generated from Generator/ClassesRef/Machine/MachineUD.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

from .lamination import Lamination
from .machine import Machine


@dataclass(eq=False)
class MachineUD(Machine):
    """User defined Machine with multiple Laminations

    Attributes
    ----------
    lam_list : [Lamination] or None
        List of Lamination
        Default: []
    is_sync : bool
        True if the machine should be handled as a Synchronous machine
        Default: True
    """

    lam_list: list[Lamination] | None = field(default_factory=list)
    """List of Lamination"""
    is_sync: bool = True
    """True if the machine should be handled as a Synchronous machine"""

    # Inlined from Methods.Machine.MachineUD.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the machine

        Parameters
        ----------
        self : MachineUD
            MachineUD object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """
        surf_list = []

        if self.frame is not None:
            surf_list.extend(
                self.frame.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )

        for lam in self.lam_list:
            surf_list.extend(lam.build_geometry(sym=sym, alpha=alpha, delta=delta))

        if self.shaft is not None:
            surf_list.extend(
                self.shaft.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )

        return surf_list

    # Inlined from Methods.Machine.MachineUD.is_synchronous
    def is_synchronous(self):
        """Return if a machine is synchronous or not

        Parameters
        ----------
        self : MachineUD
            A MachineUD

        Returns
        -------
        is_synchronous: bool
            User Defined machine are synchronous according to is_sync

        """
        return self.is_sync
