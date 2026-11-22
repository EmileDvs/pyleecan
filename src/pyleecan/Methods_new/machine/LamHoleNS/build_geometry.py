import numpy as np

from ....Classes_new.machine.lamination import Lamination
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def build_geometry(self, sym: int = 1, alpha: float = 0, delta: complex = 0, is_circular_radius: bool = False, machine: Machine | None = None) -> list:
    """Build the geometry of the LamHoleNS object

    Parameters
    ----------
    self : LamHoleNS
        The LamHoleNS to build in surface
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
    surf_list : list
        list of surfaces needed to draw the lamination

    """

    # getting the Lamination surface
    from ....Classes_new.slot.hole import Hole
    surf_list = Lamination.build_geometry(
        self, sym=sym, alpha=alpha, delta=delta, is_circular_radius=is_circular_radius
    )

    # Holes surface(s)
    ii = 0
    for hole in self.hole_north:
        # Create the first hole surface(s)
        surf_hole = hole.build_geometry(alpha=np.pi / hole.Zh, lam=self)
        surf_list.extend(
            Hole.transform_hole_surf(
                hole_surf_list=surf_hole, Zh=int(hole.Zh / 2), sym=sym, alpha=0, delta=0
            )
        )
    # Holes surface(s)
    for hole in self.hole_south:
        surf_hole = hole.build_geometry(alpha=2 * np.pi / hole.Zh, lam=self)
        surf_list.extend(
            Hole.transform_hole_surf(
                hole_surf_list=surf_hole,
                Zh=int(hole.Zh / 2),
                sym=sym,
                alpha=np.pi / hole.Zh,
                delta=0,
            )
        )

    # Apply the transformations
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
