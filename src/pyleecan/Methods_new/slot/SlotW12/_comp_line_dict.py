from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.arc_3 import Arc3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _comp_line_dict(self, lam: Lamination | Notch | None = None) -> dict:
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW12
        A SlotW12 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    line_dict: dict
        Dictionnary of the slot lines (key: line name, value: line object)
    """

    if self.is_outwards(lam=lam):
        rot_sign = True
    else:  # inward slot
        rot_sign = False

    point_dict = self._comp_point_coordinate(lam=lam)
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]
    Z5 = point_dict["Z5"]
    Z6 = point_dict["Z6"]
    Z7 = point_dict["Z7"]
    Z8 = point_dict["Z8"]

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)

    if self.R1 > 0:  # R1=0 => Z2==Z3
        line_dict["2-3"] = Arc3(begin=Z2, end=Z3, is_trigo_direction=rot_sign)
    else:
        line_dict["2-3"] = None

    if self.H1 > 0:  # H1=0 => Z3==Z4
        line_dict["3-4"] = Segment(begin=Z3, end=Z4)
    else:
        line_dict["3-4"] = None

    line_dict["4-5"] = Arc3(begin=Z4, end=Z5, is_trigo_direction=rot_sign)

    if self.H1 > 0:  # H1=0 => Z5==Z6
        line_dict["5-6"] = Segment(begin=Z5, end=Z6)
    else:
        line_dict["5-6"] = None

    if self.R1 > 0:  # R1=0 => Z6==Z7
        line_dict["6-7"] = Arc3(begin=Z6, end=Z7, is_trigo_direction=rot_sign)
    else:
        line_dict["6-7"] = None

    line_dict["7-8"] = Segment(begin=Z7, end=Z8)

    # Closing Arc
    line_dict["8-1"] = Arc1(begin=Z8, end=Z1, radius=-self.get_Rbo(lam=lam), is_trigo_direction=False)

    # Closing Active part
    line_dict["3-6"] = Segment(begin=Z3, end=Z6)
    line_dict["6-3"] = Segment(begin=Z6, end=Z3)

    return line_dict
