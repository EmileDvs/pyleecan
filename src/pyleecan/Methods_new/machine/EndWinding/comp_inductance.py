from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_inductance(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Return the enforced end winding inductance

    Parameters
    ----------
    self: EndWinding
        A EndWinding object
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    -------
    Lew : float
        end winding inductance [H]
    """

    return self.Lew_enforced
