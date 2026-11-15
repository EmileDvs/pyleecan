from ....Classes_new.geometry.segment import Segment


def build_geometry(self) -> list:
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotM19
        A SlotM19 object

    Returns
    -------
    curve_list: list
        A list of 3 Segments

    """
    point_dict = self._comp_point_coordinate()
    Z1 = point_dict["Z1"]
    Z2 = point_dict["Z2"]
    Z3 = point_dict["Z3"]
    Z4 = point_dict["Z4"]

    # Creation of curve
    curve_list = list()
    if self.H0 > 0:
        curve_list.append(Segment(begin=Z1, end=Z2))
    curve_list.append(Segment(begin=Z2, end=Z3))
    if self.H0 > 0:
        curve_list.append(Segment(begin=Z3, end=Z4))

    return curve_list
