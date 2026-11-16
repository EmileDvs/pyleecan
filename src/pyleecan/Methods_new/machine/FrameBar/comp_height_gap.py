def comp_height_gap(self) -> float:
    """Computation of the Height of the gap between the Frame and Outer Lamination

    Parameters
    ----------
    self : FrameBar
        A FrameBar object

    Returns
    -------
    Hgap: float
        Height of the Gap [m]

    """
    lam_outer = self.parent.get_lam_list()[-1]

    return self.Rint - lam_outer.Rext
