from . import VentilationPolarInstanceError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Make sure that the ventilation parameters are correctly set

    Parameters
    ----------
    self : VentilationPolar
        A VentilationPolar object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    _______
    VentilationPolarInstanceError
        Zh must be a integer
        H0 must be a float or int
        D0 must be a float or int
        Alpha0 must be a float or int
    """

    if not isinstance(self.Zh, int):
        raise VentilationPolarInstanceError("Zh must be a integer")
    if not isinstance(self.H0, float) and not isinstance(self.H0, int):
        raise VentilationPolarInstanceError("H0 must be a float or int")
    if not isinstance(self.D0, float) and not isinstance(self.D0, int):
        raise VentilationPolarInstanceError("D0 must be a float or int")
    if not isinstance(self.Alpha0, float) and not isinstance(self.Alpha0, int):
        raise VentilationPolarInstanceError("Alpha0 must be a float or int")
