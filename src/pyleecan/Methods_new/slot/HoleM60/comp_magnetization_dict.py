import numpy as np
from ....Classes_new.geometry.segment import Segment


def comp_magnetization_dict(self, is_north=True) -> dict:
    """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
    Mangetization angle with Hole centered on Ox axis

    Parameters
    ----------
    self : HoleM60
        a HoleM60 object
    is_north: True
        True: comp north magnetization, else add pi [rad]

    Returns
    -------
    mag_dict: dict
        magnetization dictionary (key=magnet_X, value=angle[rad])
    """

    # Comp magnet
    point_dict = self._comp_point_coordinate()

    mag_dict = dict()
    S0 = Segment(begin=point_dict["ZM4s"], end=point_dict["ZM3s"])
    mag_dict["magnet_0"] = S0.comp_normal()
    S1 = Segment(begin=point_dict["ZM3"], end=point_dict["ZM4"])
    mag_dict["magnet_1"] = S1.comp_normal()

    if not is_north:
        mag_dict["magnet_0"] += np.pi
        mag_dict["magnet_1"] += np.pi

    if self.magnetization_dict_offset is not None:
        for key, value in self.magnetization_dict_offset:
            mag_dict[key] += value

    return mag_dict
