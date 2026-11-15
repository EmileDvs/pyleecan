import numpy as np


def comp_alpha(self):
    """Compute the angle of the Hole (cf schematics)

    Parameters
    ----------
    self : HoleM51
        A HoleM51 object

    Returns
    -------
    alpha: float
        Angle of the Hole (cf schematics) [rad]

    """
    Rext = self.get_Rext()

    alpha = -np.arctan(
        2
        * (self.H0 - self.H1 * np.cos(0.5 * self.W1) + Rext * np.cos(0.5 * self.W1) - Rext)
        / (2.0 * self.H1 * np.sin(0.5 * self.W1) - 2 * Rext * np.sin(0.5 * self.W1) + self.W0)
    )

    return alpha
