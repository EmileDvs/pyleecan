from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_angle_d_axis(self, is_plot: bool = False, machine: Machine | None = None) -> float:
    """Compute the angle between the X axis and the first d+ axis
    By convention a "Tooth" is centered on the X axis

    Parameters
    ----------
    self : LamSlotWind
        A LamSlotWind object
    is_plot : bool
        True to plot d axis position regarding unit mmf
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    d_angle : float
        angle between the X axis and the first d+ axis
    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


    d_angle = LamSlotWind.comp_angle_d_axis(self, is_plot=is_plot)

    return d_angle
