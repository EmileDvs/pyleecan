import numpy as np


def comp_width(self):
    """Compute the width of the Hole (cf schematics)

    Parameters
    ----------
    self : HoleM51
        A HoleM51 object

    Returns
    -------
    Whole: float
        Width of the Hole (cf schematics) [m]

    """

    Rext = self.get_Rext()
    return 2 * np.sin(self.W1 / 2) * (Rext - self.H1)
