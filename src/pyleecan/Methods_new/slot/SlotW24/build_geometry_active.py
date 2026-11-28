from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import WIND_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch


def build_geometry_active(self, Nrad: int, Ntan: int, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None, lam_label: str | None = None) -> list:
    """Split the slot winding area in several zone

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object
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
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_list: list
        List of surface delimiting the winding zone

    """
    lam = container_or_parent(self, lam, "lam")

    # get the name of the lamination
    if lam_label is None:
        lam_label = lam.get_label()

    point_dict = self._comp_point_coordinate(lam=lam)
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]

    X = np.linspace(Z1, Z2, Nrad + 1)

    # Nrad+1 and Ntan+1 because 3 points => 2 zones
    Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
    for ii in range(Nrad + 1):
        Z[ii][:] = abs(X[ii]) * np.exp(
            1j * np.linspace(np.angle(X[ii]), np.angle(X[ii].conjugate()), Ntan + 1)
        )

    assert abs(Z[0][0] - Z1) < 1e-6
    assert abs(Z[Nrad][0] - Z2) < 1e-6
    assert abs(Z[0][Ntan] - Z4) < 1e-6
    assert abs(Z[Nrad][Ntan] - Z3) < 1e-6

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

    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)
    return surf_list
