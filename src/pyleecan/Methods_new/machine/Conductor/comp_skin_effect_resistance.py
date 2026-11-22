from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_skin_effect_resistance(self, freq: float | np.ndarray, T_op: float = 20, T_ref: float = 20, b: float | None = None, zt: int | None = None, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
    All parameters are defined p.270 / 271

    Parameters
    ----------
    self : Conductor
        an Conductor object
    b: float
        Slot width [m]
    zt: int
        Number of turns in series per coil
    freq: float or ndarray
        electrical frequency [Hz]
    T_op: float
        Conductor operational temperature [degC]
    T_ref: float
        Conductor reference temperature [degC]
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    ----------
    kr_skin : float
        skin effect coeff for resistance at given frequency and temperature
    """
    winding = container_or_parent(self, winding, "winding")
    lam = container_or_parent(self, lam, "lam", depth=2)

    if b is None:
        # Compute slot average width
        slot = lam.slot
        b = slot.comp_width()

    if zt is None:
        # Get number of turns in series per coil
        zt = winding.Ntcoil

    # check if wires are round or rectangular
    is_round_wire = self.is_round_wire()

    # conductor height
    hc0 = self.comp_height_wire(winding=winding, lam=lam)
    # conductor width
    bc0 = self.comp_width_wire(winding=winding, lam=lam)
    # Number of circumferential adjacent wires
    za = self.comp_nb_circumferential_wire()
    # Number of radial adjacent wires
    zp = self.comp_nb_radial_wire()
    # Equivalent height of conductor
    hc = zp * hc0

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

    # reduced conductor height Eq(5.24) p.270 + adding relative permeatibility
    ksi = hc * np.sqrt((1 / 2) * w * mu0 * mur * sigma * za * bc0 / b)

    if not isinstance(ksi, float):
        # Avoid numerical error with 0
        ksi[ksi == 0] = 1e-4

    # average resistance factor
    if is_round_wire:
        # Use round wire approximation Eq(5.30) p.271
        kr_skin = 1 + 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
    else:
        # resistance factor function phi Eq(5.26) p.271
        phi = ksi * (np.sinh(2 * ksi) + np.sin(2 * ksi)) / (np.cosh(2 * ksi) - np.cos(2 * ksi))

        # resistance factor function psi Eq(5.27) p.271
        psi = 2 * ksi * (np.sinh(ksi) - np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

        kr_skin = phi + ((zt**2 - 1) / 3) * psi  # Eq(5.28) p.271
        # kr_approx = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4  # Eq(5.29) p.271

    return kr_skin
