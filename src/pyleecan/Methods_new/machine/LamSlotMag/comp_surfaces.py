import numpy as np
from ....Classes_new.machine.lam_slot import LamSlot


def comp_surfaces(self) -> dict:
    """Compute the Lamination surfaces (Slam, Svent, Sslot, Smag)

    Parameters
    ----------
    self : LamSlotMag
        A LamSlotMag object

    Returns
    -------
    S_dict: dict
        Lamination surface dictionary (Slam, Svent, Sslot, Smag) [m**2]

    """

    S_dict = LamSlot.comp_surfaces(self)
    Smag = self.slot.comp_surface_active(lam=self)

    S_dict["Smag"] = Smag

    return S_dict
