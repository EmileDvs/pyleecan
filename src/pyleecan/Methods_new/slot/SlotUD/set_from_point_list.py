from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.arc_3 import Arc3
from ....Classes_new.geometry.segment import Segment


def set_from_point_list(self, point_list, is_sym=False):
    """Set the line_list from a point list (connected by Segments)

    Parameters
    ----------
    self : SlotUD
        A SlotUD object
    point_list : [complex]
        List of complex coordinates
    is_sym : bool
        True to duplicate the point by symmetries
    """

    # Apply symmetry if needed
    Z_list = point_list.copy()
    if is_sym:
        for point in point_list[::-1]:
            Z_list.append(point.conjugate())

    # Creation of curve
    line_list = list()
    for ii in range(len(Z_list) - 1):
        line_list.append(Segment(begin=Z_list[ii], end=Z_list[ii + 1]))

    self.line_list = line_list
