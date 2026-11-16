import numpy as np


def rotate(self, angle: float) -> None:
    """Rotate the surface

    Parameters
    ----------
    self : Trapeze
        a Trapeze Object

    angle : float
        angle for rotation [rad]


    Returns
    -------
    None
    """
    if angle == 0:
        return  # Nothing to do
    # check if the Trapeze is correct
    self.check()
    self.point_ref = self.point_ref * np.exp(1j * angle)
