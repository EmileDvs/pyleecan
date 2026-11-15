from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def _comp_line_dict(self):
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW23
        A SlotW23 object

    Returns
    -------
    line_dict: dict
        Dictionnary of the slot lines (key: line name, value: line object)
    """

    point_dict = self._comp_point_coordinate()
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
    if self.H0 > 0:
        line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    else:
        line_dict["1-2"] = None
    line_dict["2-3"] = Segment(begin=Z2, end=Z3)
    line_dict["3-4"] = Segment(begin=Z3, end=Z4)
    line_dict["4-5"] = Arc1(begin=Z4, end=Z5, radius=abs(Z5))
    line_dict["5-6"] = Segment(begin=Z5, end=Z6)
    line_dict["6-7"] = Segment(begin=Z6, end=Z7)
    if self.H0 > 0:
        line_dict["7-8"] = Segment(begin=Z7, end=Z8)
    else:
        line_dict["7-8"] = None

    # Closing Arc (Rbo)
    line_dict["8-1"] = Arc1(begin=Z8, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["3-6"] = Segment(begin=Z3, end=Z6)
    line_dict["6-3"] = Segment(begin=Z6, end=Z3)
    line_dict["7-2"] = Segment(begin=Z7, end=Z2)

    return line_dict
