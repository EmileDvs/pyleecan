from ....Classes_new.machine.lam_slot import LamSlot


def comp_surfaces(self) -> dict:
    """Compute the Lamination surfaces (Slam, Svent, Sslot, Swind)

    Parameters
    ----------
    self : LamSlotWind
        A LamSlotWind object

    Returns
    -------
    S_dict: dict
        Lamination surface dictionary (Slam, Svent, Sslot, Swind) [m**2]

    """

    S_dict = LamSlot.comp_surfaces(self)

    if self.slot is not None:
        S_dict["Swind"] = self.get_Zs() * self.slot.comp_surface_active(lam=self)
        S_dict["Swedge"] = self.get_Zs() * self.slot.comp_surface_wedges()
    else:
        S_dict["Swind"] = 0
        S_dict["Swedge"] = 0

    return S_dict
