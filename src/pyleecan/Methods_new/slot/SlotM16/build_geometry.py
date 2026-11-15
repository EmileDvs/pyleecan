from ....Classes_new.geometry.segment import Segment


def build_geometry(self):
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotM16
        A SlotM16 object

    Returns
    -------
    curve_list: list
        A list of 11 Segment

    """

    point_dict = self._comp_point_coordinate()

    # Creation of curve
    curve_list = list()
    if self.H0 > 0:
        curve_list.append(Segment(begin=point_dict["Z1"], end=point_dict["Z2"]))
    curve_list.append(Segment(begin=point_dict["Z2"], end=point_dict["Z3"]))
    if self.H1 > 0:
        curve_list.append(Segment(begin=point_dict["Z3"], end=point_dict["Z4"]))
    curve_list.append(Segment(begin=point_dict["Z4"], end=point_dict["Z5"]))
    if self.H1 > 0:
        curve_list.append(Segment(begin=point_dict["Z5"], end=point_dict["Z6"]))
    curve_list.append(Segment(begin=point_dict["Z6"], end=point_dict["Z7"]))
    if self.H0 > 0:
        curve_list.append(Segment(begin=point_dict["Z7"], end=point_dict["Z8"]))

    return curve_list
