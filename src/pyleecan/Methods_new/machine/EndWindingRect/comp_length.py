from ....classes_common.parents import container_or_parent
from ....classes_common.logger_context import get_logger
import numpy as np

from ....Classes_new.machine.lam_slot_wind import LamSlotWind
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_length(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Compute the end winding conductor length on one side for a half-turn
    excluding the straight conductor length outside of the lamination (winding.Lewout).

    Parameters
    ----------
    self: EndWindingRect
        A EndWindingRect object
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    -------
    end_wind_length : float
        End-winding length on one side for a half-turn [m].
    """
    winding = container_or_parent(self, winding, "winding")
    lam = container_or_parent(self, lam, "lam", depth=2)

    # check that Endwinding is in Winding of a Lamination with slots
    if (
        lam is None
        or not isinstance(lam, LamSlotWind)
        or lam.slot is None
    ):
        get_logger(self).warning(
            "EndWindingRect.comp_length(): "
            + "EndWindingRect has to be in a lamination with slot winding to calculate "
            + "the end winding length. Returning zero lenght."
        )
        return 0

    Rmid = lam.slot.comp_radius_mid_active()
    Zs = lam.slot.Zs
    p = winding.p

    # get the coil pitch (with some fall backs), first from the user definition
    # TODO utilize swat_em coil pitch calc.
    coil_pitch = self.coil_pitch
    if coil_pitch is None:
        # try to get coil_pitch of winding
        coil_pitch = getattr(winding, "coil_pitch", None)
        if coil_pitch is None:
            coil_pitch = Zs / p / 2
            get_logger(self).warning(
                "EndWindingCirc.comp_lenght_endwinding():"
                + "Using a coil pitch of one pole pitch for EW length calculation."
            )

    # end winding length is half the distance between two slots separated by the coil pitch
    end_wind_length = coil_pitch * np.pi / Zs * Rmid

    return end_wind_length
