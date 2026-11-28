from ....classes_common.parents import container_or_parent
import numpy as np
from . import CircleBuildGeometryError
from ....Functions_new.utils.labels import VENT_LAB

from ....Classes_new.geometry.circle import Circle
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def build_geometry(self, alpha: float = 0, delta: complex = 0, lam: Lamination | None = None, lam_label: str | None = None) -> list:
    """Compute the curve needed to plot the ventilations

    Parameters
    ----------
    self : VentilationCirc
        A VentilationCirc object
    alpha : float
        Angle for rotation (Default value = 0) [rad]
    delta : complex
        Complex for translation (Default value = 0)
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_list: list
        A list of Circle

    """
    lam = container_or_parent(self, lam, "lam")
    if lam_label is None:
        lam_label = lam.get_label()
    R_id, surf_type = self.get_R_id(lam=lam)
    RTS_id = "R" + str(R_id) + "-T0-S0"
    vent_label = lam_label + "_" + surf_type + "_" + RTS_id

    # checking if the param have good type
    if type(alpha) not in [int, float]:
        raise CircleBuildGeometryError("The parameter 'alpha' must be an int or float")
    if type(delta) not in [complex, int, float]:
        raise CircleBuildGeometryError(
            "The parameter 'delta' must be a complex or float or int number"
        )

    surf_list = list()
    # Modulo on Alpha0 for sym
    Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
    # The center
    Zc = self.H0 * np.exp(1j * Alpha0)
    # the radius of the circle on the VentilationCirc
    R = self.D0 / 2
    surf_list.append(
        Circle(
            point_ref=Zc,
            label=vent_label,
            radius=R,
            center=Zc,
        )
    )

    return surf_list
