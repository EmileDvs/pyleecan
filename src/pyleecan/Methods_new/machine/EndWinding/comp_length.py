from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_length(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Compute the end winding conductor length on one side for a half-turn
    excluding the straight conductor length outside of the lamination (winding.Lewout).
    Since this is the abstract class method the actual length returned will be zero.

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
    end_wind_length : float
        End-winding length on one side for a half-turn [m].
    """

    return 0
