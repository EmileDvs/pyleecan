import numpy as np


def comp_surface_wedge(self) -> float:
    """Compute the Slot wedge surface (by analytical computation).
    Caution, the bottom of the Slot is an Arc

    Parameters
    ----------
    self : SlotW29
        A SlotW29 object

    Returns
    -------
    S: float
        Slot wedge surface [m**2]

    """
    # Selection type Wedge
    if self.wedge_type == 0:
        return self.comp_surface_opening()

    if self.wedge_type == 1:
        return (self.W1) * self.H1

    raise NotImplementedError(f"SlotW29.wedge_type must be 0 or 1, got {self.wedge_type!r}")
