import numpy as np

from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def get_lines(self) -> list:
    """return the list of lines that delimits the PolarArc

    Parameters
    ----------
    self : PolarArc
        a PolarArc object

    Returns
    -------
    line_list: list
        List of line need to draw the slot (2 Segment + 2 Arc1)
    """
    # check if the PolarArc is correct
    self.check()

    Z_ref = self.point_ref
    center = Z_ref * np.exp(-1j * np.angle(Z_ref))
    H = self.height
    A = self.angle
    # the points of the PolarArc
    Z2 = (center - (H / 2)) * np.exp(1j * (-(A / 2))) * np.exp(1j * np.angle(Z_ref))
    Z3 = (center + (H / 2)) * np.exp(1j * (-(A / 2))) * np.exp(1j * np.angle(Z_ref))
    Z4 = (center + (H / 2)) * np.exp(1j * (A / 2)) * np.exp(1j * np.angle(Z_ref))
    Z1 = (center - (H / 2)) * np.exp(1j * (A / 2)) * np.exp(1j * np.angle(Z_ref))

    # Lines that delimit the PolarArc
    line1 = Arc1(begin=Z1, end=Z2, radius=-abs(Z1), is_trigo_direction=False)
    line2 = Segment(begin=Z2, end=Z3)
    line3 = Arc1(begin=Z3, end=Z4, radius=abs(Z3))
    line4 = Segment(begin=Z4, end=Z1)

    return [line1, line2, line3, line4]
