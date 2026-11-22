from . import VentilationTrapInstanceError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Make sure that the ventialtion parameters are correctly set

    Parameters
    ----------
    self : VentilationTrap
        A VentilationTrap object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)
    """

    if not isinstance(self.Zh, int):
        raise VentilationTrapInstanceError("Zh must be a integer")
    if not isinstance(self.H0, float) and not isinstance(self.H0, int):
        raise VentilationTrapInstanceError("H0 must be a float or int")
    if not isinstance(self.D0, float) and not isinstance(self.D0, int):
        raise VentilationTrapInstanceError("D0 must be a float or int")
    if not isinstance(self.Alpha0, float) and not isinstance(self.Alpha0, int):
        raise VentilationTrapInstanceError("Alpha0 must be a float or int")
