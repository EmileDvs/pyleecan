from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def _comp_line_dict(self) -> dict:
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW62
        A SlotW62 object

    Returns
    -------
    line_dict: dict
        Dictionnary of the slot lines (key: line name, value: line object)
    """

    Rbo = self.get_Rbo()
    point_dict = self._comp_point_coordinate()
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]
    Z5 = point_dict["Z5"]
    Z6 = point_dict["Z6"]
    Z7 = point_dict["Z7"]
    Z8 = point_dict["Z8"]

    Zw1 = point_dict["Zw1"]
    Zw2 = point_dict["Zw2"]
    Zw3 = point_dict["Zw3"]
    Zw4 = point_dict["Zw4"]

    Zw1s = point_dict["Zw1s"]
    Zw2s = point_dict["Zw2s"]
    Zw3s = point_dict["Zw3s"]
    Zw4s = point_dict["Zw4s"]

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    if Z2 != Z3:
        line_dict["2-3"] = Segment(begin=Z2, end=Z3)
    else:
        line_dict["2-3"] = None
    line_dict["3-4"] = Segment(begin=Z3, end=Z4)
    line_dict["4-5"] = Arc1(begin=Z4, end=Z5, radius=abs(Z4))
    line_dict["5-6"] = Segment(begin=Z5, end=Z6)
    if Z6 != Z7:
        line_dict["6-7"] = Segment(begin=Z6, end=Z7)
    else:
        line_dict["6-7"] = None

    line_dict["7-8"] = Segment(begin=Z7, end=Z8)
    line_dict["8-1"] = Arc1(begin=Z8, end=Z1, radius=-Rbo, is_trigo_direction=False)

    # Winding lines
    line_dict["w3-w4"] = Segment(begin=Zw3, end=Zw4)
    line_dict["w4-w1"] = Segment(begin=Zw4, end=Zw1)
    line_dict["w1-w2"] = Segment(begin=Zw1, end=Zw2)
    line_dict["w2-w3"] = Segment(begin=Zw2, end=Zw3)

    line_dict["w3s-w4s"] = Segment(begin=Zw3s, end=Zw4s)
    line_dict["w4s-w1s"] = Segment(begin=Zw4s, end=Zw1s)
    line_dict["w1s-w2s"] = Segment(begin=Zw1s, end=Zw2s)
    line_dict["w2s-w3s"] = Segment(begin=Zw2s, end=Zw3s)

    return line_dict
