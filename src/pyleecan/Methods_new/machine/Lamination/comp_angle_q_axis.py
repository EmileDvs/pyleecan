import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_angle_q_axis(self, machine: Machine | None = None) -> float:
    """Compute the angle between the X axis and the first q+ axis
    By convention a "Tooth" is centered on the X axis
    By convention the first magnet is +

    Parameters
    ----------
    self : Lamination
        A Lamination object
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    d_angle : float
        angle between the X axis and the first d+ axis
    """

    q_angle = self.comp_angle_d_axis(machine=machine)
    p = self.get_pole_pair_number()
    return q_angle + np.pi / p / 2
