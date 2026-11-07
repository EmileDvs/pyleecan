# Experimental dataclass generated from Generator/ClassesRef/Machine/CondType22.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .conductor import Conductor


@dataclass(eq=False)
class CondType22(Conductor):
    """conductor with only surface definition without specifc shape nor isolation

    Attributes
    ----------
    Sbar : float
        Surface of the Slot
        Unit: m; Default: 0.01; Minimum: 0
    """

    Sbar: float = 0.01
    """Surface of the Slot"""

    # Inlined from Methods.Machine.CondType22.comp_height_wire
    def comp_height_wire(self):
        """Return wire height

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        H: float
            Height of the bar [m]

        """

        if self.parent is not None and self.parent.parent is not None:
            Hbar = self.parent.parent.slot.comp_height()

        else:
            Hbar = np.sqrt(self.Sbar)

        return Hbar

    # Inlined from Methods.Machine.CondType22.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return 1

    # Inlined from Methods.Machine.CondType22.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return 1

    # Inlined from Methods.Machine.CondType22.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        return self.Sbar

    # Inlined from Methods.Machine.CondType22.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        return self.Sbar

    # Inlined from Methods.Machine.CondType22.comp_width_wire
    def comp_width_wire(self):
        """Return bar width

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        W: float
            Width of the bar [m]

        """

        if self.parent is not None and self.parent.parent is not None:
            Wbar = self.parent.parent.slot.comp_width()

        else:
            Wbar = np.sqrt(self.Sbar)

        return Wbar

    # Inlined from Methods.Machine.CondType22.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType22
            A CondType22 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always False since bar shape is unknown

        """

        return False
