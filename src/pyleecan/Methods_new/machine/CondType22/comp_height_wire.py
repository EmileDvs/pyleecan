import numpy as np


def comp_height_wire(self) -> float:
    """Return wire height

    Parameters
    ----------
    self : CondType22
        A CondType22 object

    Returns
    -------
    H: float
        Height of the bar [m]

    """

    if self.parent is not None and self.parent.parent is not None:
        Hbar = self.parent.parent.slot.comp_height()

    else:
        Hbar = np.sqrt(self.Sbar)

    return Hbar
