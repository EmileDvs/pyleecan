from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def build_geometry(self):
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotWLSRPM
        A SlotWLSRPM object

    Returns
    -------
    curve_list: list
        A list of 5 Segments and 2 Arcs

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
    curve_list = list()
    curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Arc1(begin=Z2, end=Z3, radius=self.R1, is_trigo_direction=True))
    curve_list.append(Segment(begin=Z3, end=Z4))
    curve_list.append(Segment(begin=Z4, end=Z5))
    curve_list.append(Segment(begin=Z5, end=Z6))
    curve_list.append(Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True))
    curve_list.append(Segment(begin=Z7, end=Z8))

    return curve_list
