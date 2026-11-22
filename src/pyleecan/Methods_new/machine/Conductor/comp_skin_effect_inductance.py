from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_skin_effect_inductance(
    self, freq: float | np.ndarray, T_op: float = 20, T_ref: float = 20, b4: float | None = None, h4: float | None = None, zt: int | None = None, winding: Winding | None = None, lam: Lamination | None = None
) -> float:
    """Compute the skin effect factor on inductance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
    All parameters bc, h4, z4, are defined in Fig(4.14) p.249

    Parameters
    ----------
    self : Conductor
        an Conductor object
    freq: float or ndarray
        electrical frequency [Hz]
    T_op: float
        Conductor operational temperature [degC]
    T_ref: float
        Conductor reference temperature [degC]
    b4: float
        Slot width [m]
    h4: float
        Slot height [m]
    zt: int
        Number of radial adjacent conductors
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    ----------
    kl_skin : float
        skin effect coeff for inductance at given frequency and temperature
    """
    winding = container_or_parent(self, winding, "winding")
    lam = container_or_parent(self, lam, "lam", depth=2)

    if b4 is None:
        # Compute slot average width
        slot = lam.slot
        b4 = slot.comp_width()

    if h4 is None:
        # Compute slot height
        slot = lam.slot
        h4 = slot.comp_height()

    if zt is None:
        # Get number of turns in series per coil
        zt = winding.Ntcoil

    # conductor width
    bc = self.comp_width_wire(winding=winding, lam=lam)

    # Electrical conductivity accounting for temperature increase
    sigma = self.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

    # Magnetic permeability
    mu0 = 4 * np.pi * 1e-7
    if self.cond_mat.mag is None or self.cond_mat.mag.mur_lin is None:
        mur = 1
    else:
        mur = self.cond_mat.mag.mur_lin

    # Electrical pulsation
    w = 2 * np.pi * freq

    # reduced conductor height Eq(4.90) p.257 + addind relative permeatibility
    ksi = h4 * np.sqrt(w * mu0 * mur * sigma * bc / (2 * b4))

    if not isinstance(ksi, float):
        # Avoid numerical error with 0
        ksi[ksi == 0] = 1e-4

    # resistance factor function phi prime Eq(4.92) p.257
    phip = (
        3 / (2 * ksi) * (np.sinh(2 * ksi) - np.sin(2 * ksi)) / (np.cosh(2 * ksi) - np.cos(2 * ksi))
    )

    # resistance factor function psi prime Eq(4.91) p.257
    psip = 1 / ksi * (np.sinh(ksi) + np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

    # average resistance factor  Eq(4.91) p.257
    kl_skin = phip / zt**2 + ((zt**2 - 1) / zt**2) * psip

    return kl_skin
