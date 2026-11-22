from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_radius(self, lam: Lamination | None = None):
    """Compute the radius of the min and max circle that contains the hole

    Parameters
    ----------
    self : HoleM58
        A HoleM58 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    (Rmin,Rmax): tuple
        Radius of the circle that contains the hole [m]
    """
    Rext = self.get_Rext(lam=lam)

    Rmax = Rext - self.H1
    Rmin = Rext - self.H0 - self.H2

    return (Rmin, Rmax)
