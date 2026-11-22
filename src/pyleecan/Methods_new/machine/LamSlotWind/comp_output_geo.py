from ....Classes_new.machine.lamination import Lamination
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.out_geo_lam import OutGeoLam


def comp_output_geo(self) -> OutGeoLam:
    """Compute the main geometry output

    Parameters
    ----------
    self : Lamination
        A Lamination object

    Returns
    -------
    output: OutGeoLam
        Main geometry output of the lamintion

    """

    output = Lamination.comp_output_geo(self)
    output.Ksfill = self.comp_fill_factor()
    if self.slot is None:
        output.S_slot = 0
        output.S_slot_wind = 0
    else:
        output.S_slot = self.slot.comp_surface(lam=self)
        output.S_slot_wind = self.slot.comp_surface_active(lam=self)
    # output.S_wind_act = self.winding.conductor.comp_surface_active()

    return output
