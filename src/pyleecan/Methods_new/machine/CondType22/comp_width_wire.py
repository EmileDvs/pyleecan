import numpy as np


def comp_width_wire(self) -> float:
    """Return bar width

    Parameters
    ----------
    self : CondType22
        A CondType22 object

    Returns
    -------
    W: float
        Width of the bar [m]

    """

    if self.parent is not None and self.parent.parent is not None:
        Wbar = self.parent.parent.slot.comp_width()

    else:
        Wbar = np.sqrt(self.Sbar)

    return Wbar
