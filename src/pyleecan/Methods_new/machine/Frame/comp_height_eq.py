def comp_height_eq(self) -> float:
    """Computation of the Frame equivalent Height for the mechanical model

    Parameters
    ----------
    self : Frame
        A Frame object

    Returns
    -------
    Hfra: float
        Equivalent Height of the Frame [m]

    """

    return self.Rext - self.Rint
