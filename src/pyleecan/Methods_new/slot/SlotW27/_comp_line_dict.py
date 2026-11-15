from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def _comp_line_dict(self):
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW27
        A SlotW27 object

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

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    line_dict["2-3"] = Segment(begin=Z2, end=Z3)
    line_dict["3-4"] = Segment(begin=Z3, end=Z4)
    line_dict["4-5"] = Segment(begin=Z4, end=Z5)
    line_dict["5-6"] = Segment(begin=Z5, end=Z6)
    line_dict["6-7"] = Segment(begin=Z6, end=Z7)
    line_dict["7-8"] = Segment(begin=Z7, end=Z8)
    line_dict["8-9"] = Segment(begin=Z8, end=Z9)
    line_dict["9-10"] = Segment(begin=Z9, end=Z10)

    # Closing Arc (Rbo)
    line_dict["10-1"] = Arc1(begin=Z10, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["2-9"] = Segment(begin=Z2, end=Z9)
    line_dict["9-2"] = Segment(begin=Z9, end=Z2)

    return line_dict
