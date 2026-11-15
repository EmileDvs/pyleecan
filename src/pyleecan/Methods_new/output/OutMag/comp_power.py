import numpy as np


def comp_power(self):
    """Compute the Ouput power

    Parameters
    ----------
    self : OutMag
        An OutMag object
    """

    if (
        self.parent is not None
        and self.parent.elec is not None
        and self.parent.elec.OP.get_N0() is not None
        and self.Tem_av is not None
    ):
        self.Pem_av = 2 * np.pi * self.parent.elec.OP.get_N0() / 60 * self.Tem_av
    else:
        self.Pem_av = None
