from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_angle_d_axis(self, machine: Machine | None = None) -> float:
    """Compute the angle between the X axis and the first d+ axis
    By convention a "Tooth" is centered on the X axis

    Parameters
    ----------
    self : LamSquirrelCage
        A LamSquirrelCage object
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    d_angle : float
        angle between the X axis and the first d+ axis
    """

    return 0
