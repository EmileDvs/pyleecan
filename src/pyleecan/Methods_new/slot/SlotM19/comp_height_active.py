import numpy as np



def comp_height_active(self) -> float:
    """Compute the height of the active area

    Parameters
    ----------
    self : SlotM19
        A SlotM19 object

    Returns
    -------
    Hwind: float
        Height of the active area [m]

    """
    return self.comp_height()
