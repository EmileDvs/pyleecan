def comp_height_yoke(self) -> float:
    """Compute the yoke height

    Parameters
    ----------
    self : LamSlotMulti
        A LamSlotMulti object

    Returns
    -------
    Hy: float
        yoke height [m]

    """
    H = 0
    for slot in self.slot_list:
        H = max(H, slot.comp_height(lam=self))
    return self.Rext - self.Rint - H
