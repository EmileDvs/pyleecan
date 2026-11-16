import numpy as np


def _comp_W(self) -> None:
    """Compute W1 and W2 method (cste tooth compatibility)

    Parameters
    ----------
    self : SlotW11
        A SlotW11 object
    Zs : int
        Number of Slot

    Returns
    -------
    None

    """
    Rbo = self.get_Rbo()

    # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
    alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

    # comp point coordinate (in complex)
    Z0 = Rbo * np.exp(1j * 0)
    Z1 = Z0 * np.exp(-1j * alpha)

    Harc = Rbo - abs(Z1.real)

    # To compute the slot width we use the fact that
    # alpha_tooth + alpha_slot = slot_pitch
    slot_pitch = 2 * np.pi / self.Zs

    # H0 and H1 are radial
    if self.is_outwards():
        radius = Rbo + self.get_H1() + self.H0
    else:
        radius = Rbo - self.get_H1() - self.H0

    alpha_T1 = float(np.arcsin(self.W3 / (2 * radius)))
    alpha_S1 = slot_pitch - 2 * alpha_T1
    self.W1 = 2 * np.tan(alpha_S1 / 2) * radius

    # define W2
    if self.is_outwards():
        self.W2 = (
            2
            * np.tan(slot_pitch / 2)
            * (
                Rbo
                - Harc
                + self.H0
                + self.get_H1()
                + self.H2
                - self.R1
                - self.W3 / (2 * np.tan(slot_pitch / 2) * np.cos(slot_pitch / 2))
            )
        )

    else:
        self.W2 = (
            2
            * np.tan(slot_pitch / 2)
            * (
                Rbo
                - Harc
                - self.H0
                - self.get_H1()
                - self.H2
                + self.R1
                + self.W3 / (2 * np.tan(slot_pitch / 2) * np.cos(slot_pitch / 2))
            )
        )
