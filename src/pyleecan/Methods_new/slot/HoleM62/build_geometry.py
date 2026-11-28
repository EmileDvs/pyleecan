from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import HOLEV_LAB, HOLEM_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.lamination import Lamination


def build_geometry(self, alpha: float = 0, delta: complex = 0, is_simplified: bool = False, lam: Lamination | None = None, lam_label: str | None = None) -> list:
    """Compute the curve (Segment) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object
    alpha : float
        Angle to rotate the slot (Default value = 0) [rad]
    delta : complex
        Complex to translate the slot (Default value = 0)
    is_simplified : bool
        True to avoid line superposition
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_list: list
        List of SurfLine needed to draw the HoleM58

    """
    lam = container_or_parent(self, lam, "lam")
    Rbo = self.get_Rbo(lam=lam)

    # Get correct label for surfaces
    if lam_label is None:
        lam_label = lam.get_label()
    R_id, surf_type = self.get_R_id(lam=lam)
    mag_label = f"{lam_label}_{HOLEM_LAB}_R{R_id}-"
    vent_label = f"{lam_label}_{surf_type}_R{R_id}-"
    point_dict = self._comp_point_coordinate(lam=lam)

    surf_list = list()
    # Create all the surfaces for all the case

    # Get all the points
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]

    # surface Hole Radial
    curve_list: list[Line] = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(
        Arc1(
            begin=Z2,
            end=Z3,
            radius=Rbo - self.H1,
            is_trigo_direction=True,
        )
    )
    curve_list.append(Segment(begin=Z3, end=Z4))
    curve_list.append(
        Arc1(
            begin=Z4,
            end=Z1,
            radius=-(abs(Z1)),
            is_trigo_direction=False,
        )
    )
    point_ref = (Z3 + Z1) / 2
    S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

    # Create the surface list by selecting the correct ones
    if self.magnet_0 is None:
        S1.label = vent_label + "T0-S0"
        surf_list = [S1]
    else:
        S1.label = mag_label + "T0-S0"
        surf_list = [S1]

    # Apply the transformations
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
