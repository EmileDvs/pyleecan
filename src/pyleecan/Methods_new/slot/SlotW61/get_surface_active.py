from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.surface import Surface
def get_surface_active(self, alpha: float = 0, delta: complex = 0) -> Surface:
    """Return the full winding surface

    Parameters
    ----------
    self : SlotW61
        A SlotW61 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)

    Returns
    -------
    surf_wind: Surface
        Surface corresponding to the Winding Area
    """

    raise Exception("get_surface_active not available for SlotW61")
