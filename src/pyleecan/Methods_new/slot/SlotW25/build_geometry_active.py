import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.labels import WIND_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line


def build_geometry_active(self, Nrad: int, Ntan: int, alpha: float = 0, delta: complex = 0) -> list:
    """Split the slot winding area in several zone

    Parameters
    ----------
    self : SlotW25
        A SlotW25 object
    Nrad : int
        Number of radial layer
    Ntan : int
        Number of tangentiel layer
    alpha : float
        Angle for rotation (Default value = 0) [rad]
    delta : Complex
        complex for translation (Default value = 0)

    Returns
    -------
    surf_list: list
        List of surface delimiting the winding zone

    """
    # get the name of the lamination
    lam_label = self.parent.get_label()

    point_dict = self._comp_point_coordinate()
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]
    Z5 = point_dict["Z5"]
    Z6 = point_dict["Z6"]
    X = np.linspace(Z3, Z4, Nrad + 1)

    # Nrad+1 and Ntan+1 because 3 points => 2 zones
    Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
    for ii in range(Nrad + 1):
        Z[ii][:] = abs(X[ii]) * np.exp(
            1j * np.linspace(np.angle(X[ii]), np.angle(X[ii].conjugate()), Ntan + 1)
        )

    if self.is_outwards():
        assert abs(Z3) < abs(Z4)
        assert abs(Z6) < abs(Z5)
    assert abs(Z[0][0] - Z3) < 1e-6
    assert abs(Z[Nrad][0] - Z4) < 1e-6
    assert abs(Z[0][Ntan] - Z6) < 1e-6
    assert abs(Z[Nrad][Ntan] - Z5) < 1e-6

    # We go thought the zone by Rad then Tan, starting by (0,0)
    surf_list = list()
    for jj in range(Ntan):  # jj from 0 to Ntan-1
        for ii in range(Nrad):  # ii from 0 to Nrad-1
            Z1 = Z[ii][jj]
            Z2 = Z[ii][jj + 1]
            Z3 = Z[ii + 1][jj + 1]
            Z4 = Z[ii + 1][jj]
            point_ref = (Z1 + Z2 + Z3 + Z4) / 4  # reference point of the surface
            # With one zone the order would be [Z7,Z4,Z5,Z6]
            curve_list: list[Line] = list()
            curve_list.append(Arc1(begin=Z1, end=Z2, radius=abs(Z1), is_trigo_direction=True))
            curve_list.append(
                Segment(
                    begin=Z2,
                    end=Z3,
                    prop_dict={DRAW_PROP_LAB: False},
                )
            )
            curve_list.append(
                Arc1(
                    begin=Z3,
                    end=Z4,
                    radius=-abs(Z3),
                    is_trigo_direction=False,
                    prop_dict={DRAW_PROP_LAB: False},
                )
            )
            curve_list.append(
                Segment(
                    begin=Z4,
                    end=Z1,
                    prop_dict={DRAW_PROP_LAB: jj != 0},
                )
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
    if Ntan == 2 and Nrad == 1:
        Z2 = point_dict["Z2"]
        Z7 = point_dict["Z7"]
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
