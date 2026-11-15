from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def _comp_line_dict(self):
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW63
        A SlotW63 object

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

    Zw1 = point_dict["Zw1"]
    Zw2 = point_dict["Zw2"]

    Zw1s = point_dict["Zw1s"]
    Zw2s = point_dict["Zw2s"]

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    line_dict["2-3"] = Segment(begin=Z2, end=Z3)
    line_dict["3-4"] = Segment(begin=Z3, end=Z4)
    line_dict["4-5"] = Segment(begin=Z4, end=Z5)
    line_dict["5-6"] = Segment(begin=Z5, end=Z6)
    line_dict["6-7"] = Segment(begin=Z6, end=Z7)
    line_dict["7-8"] = Segment(begin=Z7, end=Z8)

    # Winding lines
    line_dict["w1-2"] = Segment(begin=Zw1, end=Z2)
    line_dict["2-w1"] = Segment(begin=Z2, end=Zw1)
    line_dict["4-w2"] = Segment(begin=Z4, end=Zw2)
    line_dict["w2-w1"] = Segment(begin=Zw2, end=Zw1)
    line_dict["w1-w2"] = Segment(begin=Zw1, end=Zw2)

    line_dict["w2s-5"] = Segment(begin=Zw2s, end=Z5)
    line_dict["7-w1s"] = Segment(begin=Z7, end=Zw1s)
    line_dict["w1s-w2s"] = Segment(begin=Zw1s, end=Zw2s)

    line_dict["w1s-7"] = Segment(begin=Zw1s, end=Z7)

    line_dict["w2s-w1s"] = Segment(begin=Zw2s, end=Zw1s)
    line_dict["w2-w2s"] = Segment(begin=Zw2, end=Zw2s)

    line_dict["7-2"] = Segment(begin=Z7, end=Z2)
    line_dict["2-7"] = Segment(begin=Z2, end=Z7)

    line_dict["8-1"] = Arc1(begin=Z8, end=Z1, radius=-abs(Z8), is_trigo_direction=False)

    if self.H2 == 0:
        line_dict["7w-2w"] = Arc1(begin=Z7, end=Z2, radius=-abs(Z7), is_trigo_direction=False)

    return line_dict
