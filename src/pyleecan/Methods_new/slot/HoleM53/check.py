import numpy as np

from ..Slot import SlotCheckError
from . import S53_NoneError, S53_Rext0CheckError, S53_Rext1CheckError, S53_W4CheckError, S53_W5CheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the HoleM53 object is correct

    Parameters
    ----------
    self : HoleM53
        A HoleM53 object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    None

    Raises
    -------
    S53_Rext0CheckError
        You must have H0 < Rext
    S53_Rext1CheckError
        You must have H1 < Rext
    S53_W4CheckError
        You must have W4 < pi/2
    S53_W5CheckError
        You must have W5 >=0
    """

    # Check that everything is set
    if self.W1 is None:
        raise S53_NoneError("You must set W1 !")
    elif self.W2 is None:
        raise S53_NoneError("You must set W2 !")
    elif self.W3 is None:
        raise S53_NoneError("You must set W3 !")
    elif self.W4 is None:
        raise S53_NoneError("You must set W4 !")
    elif self.H0 is None:
        raise S53_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S53_NoneError("You must set H1 !")
    elif self.H2 is None:
        raise S53_NoneError("You must set H2 !")
    elif self.H3 is None:
        raise S53_NoneError("You must set H3 !")

    Rext = self.get_Rext(lam=lam)

    if Rext <= self.H0:
        raise S53_Rext0CheckError("You must have H0 < Rext")

    if Rext <= self.H1:
        raise S53_Rext1CheckError("You must have H1 < Rext")

    if np.pi / 2 <= self.W4:
        raise S53_W4CheckError("You must have W4 < pi/2")

    if self.comp_W5(lam=lam) < 0:
        raise S53_W5CheckError("You must have W5 >=0")

    if self.H2 < self.H3:
        raise S53_W5CheckError("You must have H3 < H2")
