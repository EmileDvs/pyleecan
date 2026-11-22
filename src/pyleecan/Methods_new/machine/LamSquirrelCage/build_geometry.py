from ....Functions_new.utils.labels import WIND_LAB, BAR_LAB

from ....Classes_new.machine.lam_slot_wind import LamSlotWind
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def build_geometry(self, sym: int = 1, alpha: float = 0, delta: complex = 0, is_circular_radius: bool = False, machine: Machine | None = None) -> list:
    """Build geometry of the LamSquirrelCage

    Parameters
    ----------
    self :
        LamSquirrelCage Object
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation
    is_circular_radius : bool
        True to add surfaces to "close" the Lamination radii
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    surf_list: list
        list of surfaces

    """
    surf_list = LamSlotWind.build_geometry(
        self, sym=sym, is_circular_radius=is_circular_radius, alpha=alpha, delta=delta
    )

    # Adapt the label
    for surf in surf_list:
        if WIND_LAB in surf.label:
            surf.label = surf.label.replace(WIND_LAB, BAR_LAB)

    return surf_list
