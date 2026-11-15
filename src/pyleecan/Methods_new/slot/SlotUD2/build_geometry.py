from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.arc_3 import Arc3
from ....Classes_new.geometry.segment import Segment


def build_geometry(self) -> list:
    """Compute the curve (Line) needed to plot the object.
    The ending point of a curve is the starting point of the next curve
    in the list

    Parameters
    ----------
    self : SlotUD2
        A SlotUD2 object

    Returns
    -------
    curve_list: list
        A list of Segments

    """

    return [line.copy() for line in self.line_list]
