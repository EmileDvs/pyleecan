import numpy as np


def get_angle(self, is_deg: bool = False) -> float:
    """Return the angle of the arc

    Parameters
    ----------
    self : Arc1
        An Arc1 object
    is_deg: bool
        True to convert to degree

    Returns
    -------
    angle: float
        Angle of the arc
    """
    # Go to center ref with begin on the X > 0 axis
    Zc = self.get_center()
    Z2 = (self.end - Zc) * np.exp(-1j * np.angle(self.begin - Zc))

    if Z2.imag > 0 and self.is_trigo_direction:
        alpha = np.angle(Z2)
    elif Z2.imag > 0 and not self.is_trigo_direction:
        alpha = -(2 * np.pi - np.angle(Z2))
    elif Z2.imag < 0 and self.is_trigo_direction:
        alpha = 2 * np.pi - abs(np.angle(Z2))
    elif Z2.imag < 0 and not self.is_trigo_direction:
        alpha = np.angle(Z2)
    elif Z2.imag == 0 and self.is_trigo_direction:
        alpha = abs(np.angle(Z2))
    elif Z2.imag == 0 and not self.is_trigo_direction:
        alpha = -abs(np.angle(Z2))
    else:
        alpha = 0

    if is_deg:
        return alpha * 180 / np.pi
    else:
        return alpha
