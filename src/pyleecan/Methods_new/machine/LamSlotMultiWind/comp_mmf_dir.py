

def comp_mmf_dir(self, current_dir: int | None = None, phase_dir: int | None = None, is_plot: bool = False) -> int:
    """Compute the rotation direction of the fundamental magnetomotive force induced by the winding

    Parameters
    ----------
    self : LamSlotMultiWind
        A LamSlotMultiWind object
    felec : float
        Stator current frequency to consider
    current_dir: int
        Stator current rotation direction +/-1
    phase_dir: int
        Stator winding phasor rotation direction +/-1
    is_plot: bool
        True to plot fft2 of stator MMF

    Returns
    -------
    mmf_dir : int
        -1 or +1
    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


    rot_dir = LamSlotWind.comp_mmf_dir(self, current_dir, phase_dir, is_plot)

    return rot_dir
