# -*- coding: utf-8 -*-

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def _comp_line_dict(self):
    """Define a dictionnary of the lines to draw the slot
    If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

    Parameters
    ----------
    self : SlotW30
        A SlotW30 object

    Returns
    -------
    line_dict: dict
        Dictionnary of the slot lines (key: line name, value: line object)
    """

    point_dict = self._comp_point_coordinate()
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    if self.R1 != 0:
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]

    else:
        Z40 = point_dict["Z40"]
        Z100 = point_dict["Z100"]

    if self.R2 != 0:
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

    else:
        Z60 = point_dict["Z60"]
        Z80 = point_dict["Z80"]

    Z11 = point_dict["Z11"]
    Z12 = point_dict["Z12"]

    # Creation of curve
    line_dict = dict()

    # Closing Arc (Rbo)
    line_dict["12-1"] = Arc1(begin=Z12, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False)

    # Closing Active part
    line_dict["2-11"] = Segment(begin=Z2, end=Z11)
    line_dict["11-2"] = Segment(begin=Z11, end=Z2)

    if self.H0 > 0:
        line_dict["1-2"] = Segment(begin=Z1, end=Z2)
        line_dict["11-12"] = Segment(begin=Z11, end=Z12)
    else:
        line_dict["1-2"] = None
        line_dict["11-12"] = None

    if self.is_outwards():
        if self.R1 != 0 and self.R2 != 0:
            line_dict["2-3"] = Segment(begin=Z2, end=Z3)
            line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=self.R1)
            line_dict["4-5"] = Segment(begin=Z4, end=Z5)
            line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=self.R2)
            line_dict["6-7"] = Segment(begin=Z6, end=Z7)
            line_dict["7-8"] = Arc1(begin=Z7, end=Z8, radius=self.R2)
            line_dict["8-9"] = Segment(begin=Z8, end=Z9)
            line_dict["9-10"] = Arc1(begin=Z9, end=Z10, radius=self.R1)
            line_dict["10-11"] = Segment(begin=Z10, end=Z11)

        elif self.R1 == 0 and self.R2 != 0:
            line_dict["2-40"] = Segment(begin=Z2, end=Z40)
            line_dict["40-5"] = Segment(begin=Z40, end=Z5)
            line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=self.R2)
            line_dict["6-7"] = Segment(begin=Z6, end=Z7)
            line_dict["7-8"] = Arc1(begin=Z7, end=Z8, radius=self.R2)
            line_dict["8-100"] = Segment(begin=Z8, end=Z100)
            line_dict["100-11"] = Segment(begin=Z100, end=Z11)

        elif self.R1 != 0 and self.R2 == 0:
            line_dict["2-3"] = Segment(begin=Z2, end=Z3)
            line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=self.R1)
            line_dict["4-60"] = Segment(begin=Z4, end=Z60)
            line_dict["60-80"] = Segment(begin=Z60, end=Z80)
            line_dict["80-9"] = Segment(begin=Z80, end=Z9)
            line_dict["9-10"] = Arc1(begin=Z9, end=Z10, radius=self.R1)
            line_dict["10-11"] = Segment(begin=Z10, end=Z11)

        elif self.R1 == 0 and self.R2 == 0:
            line_dict["2-40"] = Segment(begin=Z2, end=Z40)
            line_dict["40-60"] = Segment(begin=Z40, end=Z60)
            line_dict["60-80"] = Segment(begin=Z60, end=Z80)
            line_dict["80-100"] = Segment(begin=Z80, end=Z100)
            line_dict["100-11"] = Segment(begin=Z100, end=Z11)

    else:
        if self.R1 != 0 and self.R2 != 0:
            line_dict["2-3"] = Segment(begin=Z2, end=Z3)
            line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=-self.R1, is_trigo_direction=False)
            line_dict["4-5"] = Segment(begin=Z4, end=Z5)
            line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=-self.R2, is_trigo_direction=False)
            line_dict["6-7"] = Segment(begin=Z6, end=Z7)
            line_dict["7-8"] = Arc1(begin=Z7, end=Z8, radius=-self.R2, is_trigo_direction=False)
            line_dict["8-9"] = Segment(begin=Z8, end=Z9)
            line_dict["9-10"] = Arc1(begin=Z9, end=Z10, radius=-self.R1, is_trigo_direction=False)
            line_dict["10-11"] = Segment(begin=Z10, end=Z11)

        elif self.R1 == 0 and self.R2 != 0:
            line_dict["2-40"] = Segment(begin=Z2, end=Z40)
            line_dict["40-5"] = Segment(begin=Z40, end=Z5)
            line_dict["5-6"] = Arc1(begin=Z5, end=Z6, radius=-self.R2, is_trigo_direction=False)
            line_dict["6-7"] = Segment(begin=Z6, end=Z7)
            line_dict["7-8"] = Arc1(begin=Z7, end=Z8, radius=-self.R2, is_trigo_direction=False)
            line_dict["8-100"] = Segment(begin=Z8, end=Z100)
            line_dict["100-11"] = Segment(begin=Z100, end=Z11)

        elif self.R1 != 0 and self.R2 == 0:
            line_dict["2-3"] = Segment(begin=Z2, end=Z3)
            line_dict["3-4"] = Arc1(begin=Z3, end=Z4, radius=-self.R1, is_trigo_direction=False)
            line_dict["4-60"] = Segment(begin=Z4, end=Z60)
            line_dict["60-80"] = Segment(begin=Z60, end=Z80)
            line_dict["80-9"] = Segment(begin=Z80, end=Z9)
            line_dict["9-10"] = Arc1(begin=Z9, end=Z10, radius=-self.R1, is_trigo_direction=False)
            line_dict["10-11"] = Segment(begin=Z10, end=Z11)

        elif self.R1 == 0 and self.R2 == 0:
            line_dict["2-40"] = Segment(begin=Z2, end=Z40)
            line_dict["40-60"] = Segment(begin=Z40, end=Z60)
            line_dict["60-80"] = Segment(begin=Z60, end=Z80)
            line_dict["80-100"] = Segment(begin=Z80, end=Z100)
            line_dict["100-11"] = Segment(begin=Z100, end=Z11)

    return line_dict
