# Experimental pydantic model generated from Generator/ClassesRef/Machine/CondType22.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.parents import container_or_parent
from .conductor import Conductor

if TYPE_CHECKING:
    from .lamination import Lamination
    from .winding import Winding


class CondType22(Conductor):
    """conductor with only surface definition without specifc shape nor isolation

    Attributes
    ----------
    Sbar : float
        Surface of the Slot
        Unit: m; Default: 0.01; Minimum: 0
    """

    Sbar: float = Field(default=0.01, ge=0, json_schema_extra={"unit": "m"})
    """Surface of the Slot"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.CondType22.comp_height_wire
    def comp_height_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return wire height

        Parameters
        ----------
        self : CondType22
            A CondType22 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        H: float
            Height of the bar [m]

        """
        winding = container_or_parent(self, winding, "winding")
        lam = container_or_parent(self, lam, "lam", depth=2)

        if winding is not None and lam is not None:
            Hbar = lam.slot.comp_height()

        else:
            Hbar = np.sqrt(self.Sbar)

        return Hbar

    # Inlined from Methods.Machine.CondType22.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self) -> int:
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
    def comp_nb_radial_wire(self) -> int:
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
    def comp_surface(self) -> float:
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
    def comp_surface_active(self) -> float:
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
    def comp_width_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return bar width

        Parameters
        ----------
        self : CondType22
            A CondType22 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        W: float
            Width of the bar [m]

        """
        winding = container_or_parent(self, winding, "winding")
        lam = container_or_parent(self, lam, "lam", depth=2)

        if winding is not None and lam is not None:
            Wbar = lam.slot.comp_width()

        else:
            Wbar = np.sqrt(self.Sbar)

        return Wbar

    # Inlined from Methods.Machine.CondType22.is_round_wire
    def is_round_wire(self) -> bool:
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
