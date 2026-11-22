from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....classes_common.errors import ParentMissingError
from ....Functions_new.utils.labels import BOUNDARY_PROP_LAB, YSR_LAB, YSL_LAB, YOKE_LAB, NO_LAM_LAB, TOOTH_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.lamination import Lamination


def get_surface_tooth(self, lam: Lamination | None = None) -> SurfLine:
    """Returns the surface delimiting the tooth (including yoke part)

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    surface: SurfLine
        A SurfLine object representing the slot

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        Ryoke = lam.get_Ryoke()
    else:
        raise ParentMissingError("Error: The slot is not inside a Lamination")

    curve_list: list[Line] = list()
    # tooth lines
    top_list = self.build_geometry_half_tooth(is_top=True)
    bot_list = self.build_geometry_half_tooth(is_top=False)
    # Yoke lines
    Z1 = Ryoke * np.exp(1j * np.pi / self.Zs)
    Z2 = Ryoke * np.exp(-1j * np.pi / self.Zs)
    curve_list.append(
        Segment(begin=top_list[-1].get_end(), end=Z1, prop_dict={BOUNDARY_PROP_LAB: YSL_LAB})
    )
    if Ryoke > 0:
        curve_list.append(
            Arc1(
                begin=Z1,
                end=Z2,
                radius=-Ryoke,
                is_trigo_direction=False,
                prop_dict={BOUNDARY_PROP_LAB: YOKE_LAB},
            )
        )
    curve_list.append(
        Segment(begin=Z2, end=bot_list[0].get_begin(), prop_dict={BOUNDARY_PROP_LAB: YSR_LAB})
    )
    # Second half of the tooth
    curve_list.extend(bot_list)
    curve_list.extend(top_list)

    if lam is not None:
        lam_label = lam.get_label()
    else:
        lam_label = NO_LAM_LAB
    label = lam_label + "_" + TOOTH_LAB
    return SurfLine(line_list=curve_list, label=label)
