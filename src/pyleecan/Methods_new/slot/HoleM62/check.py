from ..Slot import SlotCheckError
from . import *
import numpy as np


def check(self):
    """Check that the HoleM62 object is correct

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object

    Returns
    -------
    None

    Raises
    _______
    S62_WCheckError
    """

    # Check that everything is set
    if self.W0 is None:
        raise S62_NoneError("You must set W0 !")
    elif self.H0 is None:
        raise S62_NoneError("You must set H0 !")
    elif self.H1 is None:
        raise S62_NoneError("You must set H1 !")
