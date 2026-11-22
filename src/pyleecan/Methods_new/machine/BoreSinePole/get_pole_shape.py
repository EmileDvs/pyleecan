from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_pole_shape(self, phi: float, lam: Lamination | None = None) -> complex:
    """Return the complex coordinates of the point at phi

    Parameters
    ----------
    self : BoreSinePole
        A BoreSinePole object
    phi : float
        Angle where to compute the point [rad]
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    Z : complex
        Coordinates of the requested point
    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        Rbo = lam.get_Rbo()
    else:
        raise ParentMissingError("Error: The slot is not inside a Lamination")

    # limit phi to valid values
    phi_max = np.arccos(self.delta_d / (self.delta_d + Rbo)) / self.k
    phi = max(-phi_max, phi)
    phi = min(phi_max, phi)

    # compute the point on the bore radius arc
    delta = self.delta_d / np.cos(phi * self.k)
    r = Rbo + self.delta_d - delta
    x = r * np.cos(2 * phi / self.N)
    y = r * np.sin(2 * phi / self.N)

    return x + 1j * y
