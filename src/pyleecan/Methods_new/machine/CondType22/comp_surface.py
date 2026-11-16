def comp_surface(self) -> float:
    """Compute the surface of the conductor

    Parameters
    ----------
    self : CondType22
        A CondType22 object

    Returns
    -------
    S: float
        Surface of the conductor (with insulation) [m**2]

    """

    return self.Sbar
