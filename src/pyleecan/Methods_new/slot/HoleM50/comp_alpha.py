import numpy as np


def comp_alpha(self):
    """Compute the alpha angle of the slot (cf schematics)

    Parameters
    ----------
    self : HoleM50
        a HoleM50 object

    Returns
    -------
    alpha: float
        Cf schematics [rad]
    """
    Rext = self.get_Rext()

    alpham = 2 * np.arcsin(self.W0 / (2 * (Rext - self.H1)))

    Harc = (Rext - self.H1) * (1 - np.cos(alpham / 2))
    return np.arctan((self.H0 - self.H1 - Harc) / (self.W0 / 2 - self.W1 / 2))
