def check(self) -> None:
    """assert the Surface is correct

    Parameters
    ----------
    self : SurfRing
        A SurfRing object

    Returns
    -------
    None
    """
    self.out_surf.check()
    self.in_surf.check()
