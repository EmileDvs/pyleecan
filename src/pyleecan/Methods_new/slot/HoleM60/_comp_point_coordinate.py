import numpy as np


def _comp_point_coordinate(self) -> dict:
    """Compute the point coordinates needed to plot the Slot.

    Parameters
    ----------
    self : HoleM60
        A HoleM60 object

    Returns
    -------
    point_dict: dict
        A dict of the slot coordinates
    """

    Rbo = self.get_Rbo()

    # comp point coordinate (in complex)
    # Draw the left side with center P
    Z0 = 1j * self.H0 / (2 * np.sin(self.W0 / 2))
    Z1 = -self.W3 / 2 + 1j * (Z0.imag + (self.W3 / 2) / np.tan(self.W0 / 2))
    Z2 = (
        Z1.real
        - np.sin(self.W0 / 2) * (self.W2 - self.H0)
        + 1j * (Z1.imag + np.cos(self.W0 / 2) * (self.W2 - self.H0))
    )

    # Draw the left hole with center P2
    Z3h = -self.H0 / 2 - 1j * self.H0 / 2
    Z4h = -1j * self.H0
    Z5h = self.W2 - self.H0 - 1j * self.H0
    Z6h = self.W2 - self.H0 / 2 - 1j * (self.H0 / 2)
    w = self.W2 - self.H0
    ZM1h = (w - self.W1) / 2 + self.W1
    ZM2h = (w - self.W1) / 2
    ZM4h = (w - self.W1) / 2 + self.W1 - 1j * self.H0
    ZM3h = (w - self.W1) / 2 - 1j * self.H0

    # Revert translation and rotation to center left hole in P
    Z3 = Z3h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    Z4 = Z4h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    Z5 = Z5h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    Z6 = Z6h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    ZM1 = ZM1h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    ZM2 = ZM2h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    ZM3 = ZM3h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
    ZM4 = ZM4h * np.exp(1j * np.angle(Z1 - Z2)) + Z2

    # Revert translation to center left hole in machine's center
    Z = 1j * (np.sqrt((Rbo - self.H1) ** 2 - Z3.real**2) - Z3.imag)
    Z0 += Z
    Z1 += Z
    Z2 += Z
    Z3 += Z
    Z4 += Z
    Z5 += Z
    Z6 += Z
    ZM1 += Z
    ZM2 += Z
    ZM3 += Z
    ZM4 += Z

    # Rotation of angle -pi / 2 to respect slot conventions
    Z *= np.exp(-1j * np.pi / 2)
    Z0 *= np.exp(-1j * np.pi / 2)
    Z1 *= np.exp(-1j * np.pi / 2)
    Z2 *= np.exp(-1j * np.pi / 2)
    Z3 *= np.exp(-1j * np.pi / 2)
    Z4 *= np.exp(-1j * np.pi / 2)
    Z5 *= np.exp(-1j * np.pi / 2)
    Z6 *= np.exp(-1j * np.pi / 2)
    ZM1 *= np.exp(-1j * np.pi / 2)
    ZM2 *= np.exp(-1j * np.pi / 2)
    ZM3 *= np.exp(-1j * np.pi / 2)
    ZM4 *= np.exp(-1j * np.pi / 2)

    # Draw the right hole by symmetry
    Z1s = Z1.conjugate()
    Z2s = Z2.conjugate()
    Z3s = Z3.conjugate()
    Z4s = Z4.conjugate()
    Z5s = Z5.conjugate()
    Z6s = Z6.conjugate()
    ZM1s = ZM1.conjugate()
    ZM2s = ZM2.conjugate()
    ZM3s = ZM3.conjugate()
    ZM4s = ZM4.conjugate()

    point_dict = dict()
    point_dict["Z"] = Z
    point_dict["Z0"] = Z0
    point_dict["Z1"] = Z1
    point_dict["Z2"] = Z2
    point_dict["Z3"] = Z3
    point_dict["Z4"] = Z4
    point_dict["Z5"] = Z5
    point_dict["Z6"] = Z6
    point_dict["ZM1"] = ZM1
    point_dict["ZM2"] = ZM2
    point_dict["ZM3"] = ZM3
    point_dict["ZM4"] = ZM4
    point_dict["Z1s"] = Z1s
    point_dict["Z2s"] = Z2s
    point_dict["Z3s"] = Z3s
    point_dict["Z4s"] = Z4s
    point_dict["Z5s"] = Z5s
    point_dict["Z6s"] = Z6s
    point_dict["ZM1s"] = ZM1s
    point_dict["ZM2s"] = ZM2s
    point_dict["ZM3s"] = ZM3s
    point_dict["ZM4s"] = ZM4s

    return point_dict
