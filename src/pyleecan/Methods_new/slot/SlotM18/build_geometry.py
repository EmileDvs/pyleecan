# -*- coding: utf-8 -*-
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1


def build_geometry(self):
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotM18
        A SlotM18 object

    Returns
    -------
    curve_list: list
        A list of 3 Segments

    """
    Rbo = self.get_Rbo()
    point_dict = self._comp_point_coordinate()
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]

    # Creation of curve
    curve_list = list()
    curve_list.append(Arc1(begin=Z1, end=Z2, radius=Rbo, is_trigo_direction=True))

    return curve_list
