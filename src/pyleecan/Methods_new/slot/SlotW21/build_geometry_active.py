from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import WIND_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch


def build_geometry_active(self, Nrad: int, Ntan: int, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None):
    """Split the slot winding area in several zone

    Parameters
    ----------
    self : SlotW21
        A SlotW21 object
    Nrad : int
        Number of radial layer
    Ntan : int
        Number of tangentiel layer
    alpha : float
        Angle for rotation (Default value = 0) [rad]
    delta : Complex
        complex for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_list:
        List of surface delimiting the winding zone

    """
    lam = container_or_parent(self, lam, "lam")

    # get the name of the lamination
    lam_label = lam.get_label()

    point_dict = self._comp_point_coordinate()
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]
    Z5 = point_dict["Z5"]
    Z6 = point_dict["Z6"]
    Z7 = point_dict["Z7"]
    X = np.linspace(Z3, Z4, Nrad + 1)

    # Nrad+1 and Ntan+1 because 3 points => 2 zones
    Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
    for ii in range(Nrad + 1):
        Z[ii][:] = np.linspace(X[ii], X[ii].conjugate(), Ntan + 1)

    assert Z[0][0] == Z3
    assert Z[Nrad][0] == Z4
    assert Z[0][Ntan] == Z6
    assert Z[Nrad][Ntan] == Z5

    # We go thought the zone by Rad then Tan, starting by (0,0)
    surf_list = list()
    for jj in range(Ntan):  # jj from 0 to Ntan-1
        for ii in range(Nrad):  # ii from 0 to Nrad-1
            point_ref = (
                Z[ii][jj] + Z[ii][jj + 1] + Z[ii + 1][jj + 1] + Z[ii + 1][jj]
            ) / 4  # tre reference point of the surface
            # With one zone the order would be [Z6,Z3,Z4,Z5]
            curve_list: list[Line] = list()
            curve_list.append(Segment(begin=Z[ii][jj], end=Z[ii][jj + 1]))
            curve_list.append(
                Segment(
                    begin=Z[ii][jj + 1], end=Z[ii + 1][jj + 1], prop_dict={DRAW_PROP_LAB: False}
                )
            )
            curve_list.append(
                Segment(
                    begin=Z[ii + 1][jj + 1], end=Z[ii + 1][jj], prop_dict={DRAW_PROP_LAB: False}
                )
            )
            curve_list.append(
                Segment(begin=Z[ii + 1][jj], end=Z[ii][jj], prop_dict={DRAW_PROP_LAB: jj != 0})
            )
            surface = SurfLine(
                line_list=curve_list,
                label=lam_label
                + "_"
                + WIND_LAB
                + "_R"
                + str(ii)
                + "-T"
                + str(jj)
                + "-S0",
                point_ref=point_ref,
            )
            surf_list.append(surface)

    # Correct bottom line for particular case (cf Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
    if Ntan == 2 and Nrad == 1 and self.W1 != self.W0 and self.H1 == 0:
        # Cut Ox- surface
        arc_to_cut = surf_list[0].line_list[0]
        arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z2)
        surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
        surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
        # Cut Ox+ surface
        arc_to_cut = surf_list[1].line_list[0]
        arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z7)
        surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
        surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)
    return surf_list
