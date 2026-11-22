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
    self : HoleM52R
        a HoleM52R object
    is_north: True
        True: comp north magnetization, else add pi [rad]
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    mag_dict: dict
        magnetization dictionary (key=magnet_X, value=angle[rad])
    """

    # Comp magnet
    point_dict = self._comp_point_coordinate(lam=lam)

    mag_dict = dict()
    S0 = Segment(begin=point_dict["Z4"], end=point_dict["Z6"])
    mag_dict["magnet_0"] = S0.comp_normal()

    if not is_north:
        mag_dict["magnet_0"] += np.pi

    if self.magnetization_dict_offset is not None:
        for key, value in self.magnetization_dict_offset:
            mag_dict[key] += value

    return mag_dict
