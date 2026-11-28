import numpy as np

from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None, lam_label: str | None = None) -> Surface:
    """Return the full winding surface

    Parameters
    ----------
    self : SlotUD2
        A SlotUD2 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_wind: Surface
        Surface corresponding to the Winding Area
    """
    st = self.get_name_lam(lam=lam, lam_label=lam_label)
    surface = self.active_surf.copy()

    surface.label = "Wind_" + st + "_R0_T0_S0"

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
