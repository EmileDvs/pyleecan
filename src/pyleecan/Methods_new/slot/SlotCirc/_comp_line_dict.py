from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_line_dict(self, lam: Lamination | Notch | None = None) -> dict:
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotCirc
        A SlotCirc object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    line_dict: dict
        Dictionnary of the slot lines (key: line name, value: line object)
    """

    point_dict = self._comp_point_coordinate(lam=lam)
    R0 = self._comp_R0(lam=lam)

    if self.H0 < self.W0 / 2:
        sign = -1
    else:
        sign = 1
    # Creation of curve
    if self.is_outwards(lam=lam):
        full_arc = Arc1(
            begin=point_dict["Z1"],
            end=point_dict["Z2"],
            radius=-R0 * sign,
            is_trigo_direction=True,
        )
    else:
        full_arc = Arc1(
            begin=point_dict["Z1"],
            end=point_dict["Z2"],
            radius=R0 * sign,
            is_trigo_direction=False,
        )

    line_dict = dict()
    line_dict["1-2"] = full_arc
    # Split arc to avoid angle > 180 deg (for FEMM)
    line_dict["1-M"] = full_arc.copy()
    line_dict["1-M"].split_half(is_begin=True)
    line_dict["M-2"] = full_arc.copy()
    line_dict["M-2"].split_half(is_begin=False)
    # Closing arc
    line_dict["2-1"] = Arc1(
        begin=point_dict["Z2"], end=point_dict["Z1"], radius=-self.get_Rbo(lam=lam), is_trigo_direction=False
    )

    return line_dict
