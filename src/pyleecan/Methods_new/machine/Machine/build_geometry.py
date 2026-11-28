def build_geometry(self, sym: int = 1, alpha: float = 0, delta: complex = 0) -> list:
    """Build the geometry of the machine

    Parameters
    ----------
    self : Machine
        Machine object
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation

    Returns
    -------
    surf_list : list
        list of surfaces needed to draw the lamination

    """
    surf_list = list()

    if self.frame is not None:
        surf_list.extend(self.frame.build_geometry(sym=sym, alpha=alpha, delta=delta))

    if self.rotor.is_internal:
        # Adding the list of surfaces of the stator
        surf_list.extend(self.stator.build_geometry(sym=sym, alpha=alpha, delta=delta, machine=self))
        # Adding the list of surfaces of the rotor
        surf_list.extend(self.rotor.build_geometry(sym=sym, alpha=alpha, delta=delta, machine=self))
        # Add the shaft only for Internal Rotor
        if self.rotor.Rint > 0:
            surf_list.extend(
                self.shaft.build_geometry(sym=sym, alpha=alpha, delta=delta)
            )
    else:
        # Adding the list of surfaces of the rotor
        surf_list.extend(self.rotor.build_geometry(sym=sym, alpha=alpha, delta=delta, machine=self))
        # Adding the list of surfaces of the stator
        surf_list.extend(self.stator.build_geometry(sym=sym, alpha=alpha, delta=delta, machine=self))

    return surf_list
