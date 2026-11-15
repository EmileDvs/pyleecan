import numpy as np

from ....Classes_new.geometry.circle import Circle
from ....Classes_new.geometry.surf_line import SurfLine
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment


def get_Zs(self):
    """Return the number of Slot of the Lamination

    Parameters
    ----------
    self : LamSlotMulti
        a LamSlotMulti object

    Returns
    -------
    Zs : float
        Number of Slot

    """

    return len(self.slot_list)
