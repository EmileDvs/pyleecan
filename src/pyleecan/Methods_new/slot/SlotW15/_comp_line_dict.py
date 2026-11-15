from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def _comp_line_dict(self):
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW15
        A SlotW15 object

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
    Z9 = point_dict["Z9"]
    Z10 = point_dict["Z10"]
    Z11 = point_dict["Z11"]
    Z12 = point_dict["Z12"]
    Z13 = point_dict["Z13"]

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    line_dict["2-3"] = Segment(begin=Z2, end=Z3)
    line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=self.R1)
    line_dict["4-5"] = Segment(begin=Z4, end=Z5)
    line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=self.R2)
    line_dict["6-8"] = Arc1(begin=Z6, end=Z8, radius=abs(Z7))
    line_dict["8-9"] = Arc1(begin=Z8, end=Z9, radius=self.R2)
    line_dict["9-10"] = Segment(begin=Z9, end=Z10)
    line_dict["10-11"] = Arc1(begin=Z10, end=Z11, radius=self.R1)
    line_dict["11-12"] = Segment(begin=Z11, end=Z12)
    line_dict["12-13"] = Segment(begin=Z12, end=Z13)

    # Closing Arc (Rbo)
    line_dict["13-1"] = Arc1(begin=Z13, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["2-12"] = Segment(begin=Z2, end=Z12)
    line_dict["12-2"] = Segment(begin=Z12, end=Z2)

    return line_dict
