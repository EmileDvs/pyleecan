from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND
    from ....Classes_new.machine.machine import Machine


def comp_mmf_unit(self, Na: int, Nt: int, felec: float = 1, current_dir: int | None = None, phase_dir: int | None = None, machine: Machine | None = None) -> tuple[DataND, DataND]:
    """Compute the winding Unit magnetomotive force

    Parameters
    ----------
    self : LamSlotMultiWind
        an LamSlotMultiWind object
    Na : int
        Space discretization for offline computation (otherwise use out.elec.angle)
    Nt : int
        Time discretization for offline computation (otherwise use out.elec.time)
    felec : float
        Stator current frequency to consider
    current_dir: int
        Stator current rotation direction +/-1
    phase_dir: int
        Stator winding phasor rotation direction +/-1
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    MMF_U : DataND
        Unit magnetomotive force (Na,Nt)
    WF : DataND
        Winding functions (qs,Na)

    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


    MMF_U, WF = LamSlotWind.comp_mmf_unit(
        self, Na=Na, Nt=Nt, felec=felec, current_dir=current_dir, phase_dir=phase_dir
    )

    return MMF_U, WF
