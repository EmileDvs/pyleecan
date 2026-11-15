from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def _comp_line_dict(self) -> dict:
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object

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
    Zc = 0

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    line_dict["2-3"] = Arc1(begin=Z2, end=Z3, radius=abs(Z2))
    line_dict["3-4"] = Segment(begin=Z3, end=Z4)

    # Closing Arc (Rbo)
    line_dict["4-1"] = Arc1(begin=Z4, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["1-4"] = Arc1(begin=Z1, end=Z4, radius=self.get_Rbo(), is_trigo_direction=True)

    return line_dict
