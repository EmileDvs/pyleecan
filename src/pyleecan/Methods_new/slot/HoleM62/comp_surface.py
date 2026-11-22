import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of the Hole

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    S: float
        Surface of the Hole. [m**2]

    """
    Rbo = self.get_Rbo(lam=lam)
    if self.W0_is_rad:  # Polar Arc
        return (
            self.W0 * (Rbo - self.H1) ** 2 / 2
            - self.W0 * (Rbo - self.H1 - self.H0) ** 2 / 2
        )

    else:  # Parallel side
        Rbo = self.get_Rbo(lam=lam)
        # Top surface
        alpha = 2 * np.arcsin((self.W0 / 2) / (Rbo - self.H1))
        Stop = ((Rbo - self.H1) ** 2) * (alpha - np.sin(alpha)) / 2

        # Bottom surface
        point_dict = self._comp_point_coordinate(lam=lam)
        Z1 = point_dict["Z1"]
        R1 = abs(Z1)
        alpha = 2 * np.arcsin((self.W0 / 2) / R1)
        Sbot = R1**2 * (alpha - np.sin(alpha)) / 2

        return self.H0 * self.W0 + Stop - Sbot
