import numpy as np

from ....Classes_new.machine.lamination import Lamination
from ....Classes_new.geometry.circle import Circle
from ....Classes_new.geometry.surf_line import SurfLine
from ....Classes_new.geometry.surf_ring import SurfRing
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Functions_new.labels import update_RTS_index


def build_geometry(self, sym: int = 1, alpha: float = 0, delta: complex = 0, is_circular_radius: bool = False) -> list:
    """Build the geometry of the LamHole object

    Parameters
    ----------
    self : LamHole
        The LamHole to build in surface
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation
    is_circular_radius : bool
        True to add surfaces to "close" the Lamination radii

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
    for hole in self.hole:
        # Create the first hole surface(s)
        surf_hole = hole.build_geometry(alpha=np.pi / hole.Zh)
        surf_list.extend(
            Hole.transform_hole_surf(
                hole_surf_list=surf_hole, Zh=hole.Zh, sym=sym, alpha=0, delta=0
            )
        )

    # Apply the transformations
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
