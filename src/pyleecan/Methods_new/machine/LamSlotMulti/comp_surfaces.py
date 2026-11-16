import numpy as np
from ....Classes_new.machine.lamination import Lamination


def comp_surfaces(self) -> dict:
    """Compute the Lamination surfaces (Lamination, Ventilation, Slot).

    Parameters
    ----------
    self : LamSlotMulti
        A LamSlotMulti object

    Returns
    -------
    S_dict: dict
        Lamination surface dictionary (Slam, Svent, Sslot) [m**2]

    """

    S_dict = Lamination.comp_surfaces(self)
    Sslot = 0
    for slot in self.slot_list:
        Sslot += slot.comp_surface()

    S_dict["Sslot"] = Sslot
    S_dict["Slam"] -= Sslot
    return S_dict
