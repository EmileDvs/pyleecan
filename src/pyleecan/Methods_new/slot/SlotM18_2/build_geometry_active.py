from ....classes_common.parents import container_or_parent
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import WIND_LAB, COND_BOUNDARY_PROP_LAB, YSMR_LAB, YSML_LAB, YOKE_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch


def build_geometry_active(self, Nrad: int, Ntan: int, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> list:
    """Split the slot active area in several zone

    Parameters
    ----------
    self : SlotM18_2
        A SlotM18_2 object
    Nrad : int
        Number of radial layer
    Ntan : int
        Number of tangentiel layer
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_list: list
        List of surface delimiting the active zone

    """
    lam = container_or_parent(self, lam, "lam")

    # get the name of the lamination
    lam_label = lam.get_label()
    Rbo = self.get_Rbo(lam=lam)

    if Nrad == 1 and Ntan == 1:
        surf_list = [self.get_surface_active(lam=lam)]
        surf_list[0].label = lam_label + "_" + WIND_LAB + "_R0-T0-S0"
    elif Nrad == 2 and Ntan == 1:
        point_dict = self._comp_point_coordinate(lam=lam)
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]
        ZM5 = point_dict["ZM5"]
        ZM6 = point_dict["ZM6"]

        # Bore Magnet
        surf_list = list()
        curve_list: list[Line] = list()
        curve_list.append(
            Segment(begin=ZM1, end=ZM2, prop_dict={COND_BOUNDARY_PROP_LAB: YSMR_LAB})
        )

        if self.is_outwards(lam=lam):
            curve_list.append(
                Arc1(begin=ZM2, end=ZM5, radius=(Rbo - self.H0_bore), is_trigo_direction=True)
            )
        else:
            curve_list.append(
                Arc1(begin=ZM2, end=ZM5, radius=(Rbo + self.H0_bore), is_trigo_direction=True)
            )

        curve_list.append(
            Segment(begin=ZM5, end=ZM6, prop_dict={COND_BOUNDARY_PROP_LAB: YSML_LAB})
        )

        if self.is_outwards(lam=lam):
            curve_list.append(Arc1(begin=ZM6, end=ZM1, radius=-Rbo, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(begin=ZM6, end=ZM1, radius=-Rbo, is_trigo_direction=False))
        # If no lamination, BC is required on bore
        curve_list[-1].prop_dict = {COND_BOUNDARY_PROP_LAB: YOKE_LAB}

        Zmid = (abs(ZM1) + abs(ZM2)) / 2

        surf_list.append(
            SurfLine(
                line_list=curve_list,
                label=lam_label + "_" + WIND_LAB + "_R0-T0-S0",
                point_ref=Zmid,
            )
        )

        # Airgap magnet
        curve_list = list()
        curve_list.append(
            Segment(begin=ZM2, end=ZM3, prop_dict={COND_BOUNDARY_PROP_LAB: YSMR_LAB})
        )

        if self.is_outwards(lam=lam):
            curve_list.append(
                Arc1(
                    begin=ZM3,
                    end=ZM4,
                    radius=(Rbo - self.H0_bore - self.H0_gap),
                    is_trigo_direction=True,
                )
            )
        else:
            curve_list.append(
                Arc1(
                    begin=ZM3,
                    end=ZM4,
                    radius=(Rbo + self.H0_bore + self.H0_gap),
                    is_trigo_direction=True,
                )
            )

        curve_list.append(
            Segment(begin=ZM4, end=ZM5, prop_dict={COND_BOUNDARY_PROP_LAB: YSML_LAB})
        )

        if self.is_outwards(lam=lam):
            curve_list.append(
                Arc1(begin=ZM5, end=ZM2, radius=-Rbo + self.H0_bore, is_trigo_direction=False)
            )
        else:
            curve_list.append(
                Arc1(begin=ZM5, end=ZM2, radius=-Rbo - self.H0_bore, is_trigo_direction=False)
            )

        Zmid = (abs(ZM2) + abs(ZM3)) / 2

        surf_list.append(
            SurfLine(
                line_list=curve_list,
                label=lam_label + "_" + WIND_LAB + "_R1-T0-S0",
                point_ref=Zmid,
            )
        )
    else:
        raise Exception(
            "Error Nrad=" + str(Nrad) + ", Ntan=" + str(Ntan) + ", is not available"
        )

    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)
    return surf_list
