from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def _comp_line_dict(self) -> dict:
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW16
        A SlotW16 object

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
    Z9 = point_dict["Z9"]
    Z10 = point_dict["Z10"]

    # Creation of curve
    line_dict = dict()
    line_dict["1-2"] = Segment(begin=Z1, end=Z2)
    line_dict["2-3"] = Arc1(begin=Z2, end=Z3, radius=-Rbo + self.H0, is_trigo_direction=False)
    line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=-self.R1, is_trigo_direction=False)
    line_dict["4-5"] = Segment(begin=Z4, end=Z5)
    line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=Rbo - self.H0 - self.H2, is_trigo_direction=True)
    line_dict["6-7"] = Segment(begin=Z6, end=Z7)
    line_dict["7-8"] = Arc1(begin=Z7, end=Z8, radius=-self.R1, is_trigo_direction=False)
    line_dict["8-9"] = Arc1(begin=Z8, end=Z9, radius=-Rbo + self.H0, is_trigo_direction=False)
    line_dict["9-10"] = Segment(begin=Z9, end=Z10)

    # Closing Arc (Rbo)
    line_dict["10-1"] = Arc1(begin=Z10, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["9-2"] = Arc1(
        begin=Z9,
        end=Z2,
        radius=-abs(Z9),
        is_trigo_direction=False,
    )
    line_dict["2-9"] = Arc1(
        begin=Z2,
        end=Z9,
        radius=abs(Z9),
        is_trigo_direction=True,
    )

    return line_dict
