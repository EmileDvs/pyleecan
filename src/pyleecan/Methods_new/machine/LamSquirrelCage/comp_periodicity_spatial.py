

def comp_periodicity_spatial(self) -> tuple[int | None, bool]:
    """Compute the periodicity factor of the lamination

    Parameters
    ----------
    self : LamSquirrelCage
        A LamSquirrelCage object

    Returns
    -------
    per_a : int
        Number of spatial periodicities of the lamination
    is_antiper_a : bool
        True if an spatial anti-periodicity is possible after the periodicities
    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lamination import Lamination


    per_a, is_antiper_a = Lamination.comp_periodicity_spatial(self)

    return per_a, is_antiper_a
