from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.winding import Winding


def comp_height_wire(self, winding: Winding | None = None, lam: Lamination | None = None) -> float:
    """Return wire height

    Parameters
    ----------
    self : CondType11
        A CondType11 object
    winding : Winding, optional
        Winding holding the object (default: the parent)
    lam : Lamination, optional
        Lamination of the winding (default: the parent of the winding)

    Returns
    -------
    H: float
        Height of the wire [m]

    """

    return self.Hwire
