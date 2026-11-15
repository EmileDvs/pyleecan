# -*- coding: utf-8 -*-

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def build_geometry(self):
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotDC
        A SlotDC object

    Returns
    -------
    curve_list: list
        A list of 6 Segment and 5 Arc

    """

    [
        Z1,
        Z2,
        Z3,
        Z4,
        Z5,
        Z6,
        Z7,
        Z8,
        Z9,
        Z10,
        Z11,
        Z12,
        _,
        _,
        _,
    ] = self._comp_point_coordinate()

    # Adapt the lines according to the lamination
    if self.is_outwards():
        sign = 1
        direc = True
    else:
        sign = -1
        direc = False

    # Creation of curve
    curve_list = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Arc1(begin=Z2, end=Z3, radius=sign * self.D1 / 2, is_trigo_direction=direc))
    curve_list.append(Segment(begin=Z3, end=Z4))
    curve_list.append(Arc1(begin=Z4, end=Z5, radius=sign * self.D2 / 2, is_trigo_direction=direc))
    curve_list.append(Segment(begin=Z5, end=Z6))

    curve_list.append(Arc1(begin=Z6, end=Z7, radius=sign * self.R3, is_trigo_direction=direc))

    curve_list.append(Segment(begin=Z7, end=Z8))
    curve_list.append(Arc1(begin=Z8, end=Z9, radius=sign * self.D2 / 2, is_trigo_direction=direc))
    curve_list.append(Segment(begin=Z9, end=Z10))
    curve_list.append(Arc1(begin=Z10, end=Z11, radius=sign * self.D1 / 2, is_trigo_direction=direc))
    curve_list.append(Segment(begin=Z11, end=Z12))

    return curve_list
