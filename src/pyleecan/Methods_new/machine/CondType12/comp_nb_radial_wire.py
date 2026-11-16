import numpy as np


def comp_nb_radial_wire(self) -> int:
    """Return number of adjacent wires in radial direction

    Parameters
    ----------
    self : CondType12
        A CondType12 object

    Returns
    -------
    Nwppc_rad: int
        Number of adjacent wires in radial direction

    """

    return int(np.sqrt(self.Nwppc))
