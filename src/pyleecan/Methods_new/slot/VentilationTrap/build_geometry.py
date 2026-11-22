from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.geometry.trapeze import Trapeze
from . import TrapezeBuildGeometryError
from ....Functions_new.utils.labels import VENT_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def build_geometry(self, alpha: float = 0, delta: complex = 0, lam: Lamination | None = None) -> list:
    """Compute the curve needed to plot the ventilations

    Parameters
    ----------
    self : VentilationTrap
        A VentilationTrap object
    alpha : float
        Angle for rotation (Default value = 0) [rad]
    delta : complex
        Complex for translation (Default value = 0)
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    surf_list: list
        A list of Trapeze
    """
    lam = container_or_parent(self, lam, "lam")

    lam_label = lam.get_label()
    R_id, surf_type = self.get_R_id(lam=lam)
    RTS_id = "R" + str(R_id) + "-T0-S0"
    vent_label = lam_label + "_" + surf_type + "_" + RTS_id

    # checking if the param have good type
    if type(alpha) not in [int, float]:
        raise TrapezeBuildGeometryError("The parameter 'alpha' must be an int or float")
    if type(delta) not in [complex, int, float]:
        raise TrapezeBuildGeometryError(
            "The parameter 'delta' must be a complex or float or int number"
        )

    surf_list = list()
    # Modulo on Alpha for sym
    Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
    Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * Alpha0)
    surf_list.append(
        Trapeze(
            point_ref=Zc,
            label=vent_label,
            height=self.D0,
            W1=self.W1,
            W2=self.W2,
        )
    )
    return surf_list
