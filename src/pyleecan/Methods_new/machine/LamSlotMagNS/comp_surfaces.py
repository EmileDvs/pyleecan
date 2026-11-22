import numpy as np
from ....Classes_new.machine.lam_slot import LamSlot


def comp_surfaces(self) -> dict:
    """Compute the Lamination surfaces (Slam, Svent, Sslot, Smag)

    Parameters
    ----------
    self : LamSlotMagNS
        A LamSlotMagNS object

    Returns
    -------
    S_dict: dict
        Lamination surface dictionary (Slam, Svent, Sslot, Smag) [m**2]

    """

    S_dict = LamSlot.comp_surfaces(self)
    Smag = 0
    if self.magnet_north is not None:
        Smag += self.slot.comp_surface_active(lam=self)
    if self.magnet_south is not None:
        Smag += self.slot_south.comp_surface_active(lam=self)

    S_dict["Smag"] = Smag

    return S_dict
