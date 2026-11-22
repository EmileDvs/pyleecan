from ....Classes_new.slot.slot_w_22 import SlotW22
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


def get_polar_eq(self) -> LamSlotWind:
    """Returns a polar equivalent of the lamination

    Parameters
    ----------
    self : LamSlotWind
        A LamSlotWind object to convert to polar

    Returns
    -------
    polar_eq: LamSlotWind
        The polar equivalent of the lamination
    """

    # Copy the lamination
    polar_eq = type(self)(init_dict=self.as_dict())

    # Compute the polar dimension of the slot
    Hwind = self.slot.comp_height_active(lam=self)
    Histhmus = self.slot.comp_height(lam=self) - Hwind
    Wwind = self.slot.comp_angle_active_eq(lam=self)
    Wisthmus = self.slot.comp_angle_opening(lam=self)

    polar_eq.slot = SlotW22(
        Zs=self.slot.Zs, H0=Histhmus, W0=Wisthmus, H2=Hwind, W2=Wwind
    )

    # TODO: Polar eq for ventilations ?
    polar_eq.axial_vent = list()

    return polar_eq
