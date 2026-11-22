import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_angle_d_axis(self, machine: Machine | None = None) -> float:
    """Compute the angle between the X axis and the first d+ axis
    By convention a "Tooth" is centered on the X axis
    By convention the first magnet is +

    Parameters
    ----------
    self : LamSlotM
        A LamSlotM object
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    d_angle : float
        angle between the X axis and the first d+ axis
    """

    angle = np.pi / self.get_pole_pair_number() / 2

    if self.has_magnet():
        if hasattr(self, "magnet") and self.magnet.type_magnetization == 3:
            angle = 0
        elif (
            hasattr(self, "magnet_north")
            and hasattr(self, "magnet_south")
            and self.magnet_north.type_magnetization == 3
            and self.magnet_south.type_magnetization == 3
        ):
            angle = 0

    return angle
