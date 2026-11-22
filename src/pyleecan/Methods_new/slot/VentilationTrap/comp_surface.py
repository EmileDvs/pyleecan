from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Compute the surface of all the axial ventilation ducts

    Parameters
    ----------
    self : VentilationTrap
        A VentilationTrap object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    surface: float
        Axial ventilation ducts total surface [m**2]

    """

    self.check(lam=lam)

    return (self.W1 + self.W2) * 0.5 * self.D0
