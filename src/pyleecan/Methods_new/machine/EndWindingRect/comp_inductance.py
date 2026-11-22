from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_inductance(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Compute the end winding inductance based on permeance coefficient stored in EndWindingRect object
    from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition

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
    Lew : float
        end winding inductance [H].
    """
    winding = container_or_parent(self, winding, "winding")

    if winding is None:
        return 0

    p = winding.p
    Ntcoil = winding.Ntcoil

    mu0 = 4 * np.pi * 1e-7

    if winding.Lewout is not None:
        l_ew = winding.Lewout
    else:
        l_ew = 0

    # Calculate width of end winding
    w_ew = 2 * self.comp_length(winding=winding, lam=lam)

    # Calculate Eq(4.100)
    l_lambda = 2 * l_ew * self.lambda_length + w_ew * self.lambda_width

    # Calculate end-winding inductance from Eq (4.98) p.261
    Lw = 2 / p * Ntcoil**2 * mu0 * l_lambda

    return Lw
