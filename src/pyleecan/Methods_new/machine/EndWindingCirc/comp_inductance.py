from ....classes_common.parents import container_or_parent
from ....classes_common.logger_context import get_logger
import numpy as np

from ....Classes_new.machine.lam_slot_wind import LamSlotWind
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_inductance(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Compute the end winding inductance from "Design of Brushless Permanent-Magnet Machines", J.R Henderson, 2010

    Parameters
    ----------
    self: EndWinding
        A EndWinding object
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    -------
    Lew : float
        end winding inductance [H].
    """
    winding = container_or_parent(self, winding, "winding")
    lam = container_or_parent(self, lam, "lam", depth=2)

    # ckeck that Endwinding is in Winding of a Lamination with slots
    if (
        lam is None
        or not isinstance(lam, LamSlotWind)
        or lam.slot is None
    ):
        get_logger(self).warning(
            "EndWindingCirc.comp_inductance(): "
            + "EndWindingCirc has to be in a lamination with slot winding to calculate "
            + "the end winding inductance. Returning zero inductance."
        )
        return 0

    # get the middle radius of the slots active area
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
                "EndWindingCirc.comp_inductance():"
                + "Using a coil pitch of one pole pitch for EW inductance calculation."
            )

    # End winding is a circle whose radius is half the coil pitch distance
    Re = np.pi / Zs * Rmid * coil_pitch

    # Eq(5.49) p.234
    Scond = winding.conductor.comp_surface()
    R = 0.4394 * np.sqrt(Scond)

    # Eq (5.48) p 233
    Ntcoil = winding.Ntcoil
    mu0 = 4 * np.pi * 1e-7
    Lw = mu0 * Re * Ntcoil**2 * (np.log(8 * Re / R) - 2)

    return Lw
