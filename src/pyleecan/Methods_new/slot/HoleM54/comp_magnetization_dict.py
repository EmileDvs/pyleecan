import numpy as np
from ....Classes_new.geometry.segment import Segment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_magnetization_dict(self, is_north=True, lam: Lamination | None = None) -> dict:
    """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
    Mangetization angle with Hole centered on Ox axis

    Parameters
    ----------
    self : HoleM54
        a HoleM54 object
    is_north: True
        True: comp north magnetization, else add pi [rad]
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    mag_dict: dict
        magnetization dictionary (key=magnet_X, value=angle[rad])
    """

    mag_dict = dict()

    return mag_dict
