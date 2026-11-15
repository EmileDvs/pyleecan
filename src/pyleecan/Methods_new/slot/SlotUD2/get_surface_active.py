import numpy as np

from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.surface import Surface


def get_surface_active(self, alpha: float = 0, delta: complex = 0) -> Surface:
    """Return the full winding surface

    Parameters
    ----------
    self : SlotUD2
        A SlotUD2 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)

    Returns
    -------
    surf_wind: Surface
        Surface corresponding to the Winding Area
    """
    st = self.get_name_lam()
    surface = self.active_surf.copy()

    surface.label = "Wind_" + st + "_R0_T0_S0"

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return surface
