from . import AbstractClassError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.lut_dq import LUTdq


def update_from_ref(self, LUT_ref: LUTdq):
    """Compute and set the parameter attributes of the EEC from a reference LUT

    Parameters
    ----------
    self : EEC
        an EEC object
    LUT_ref : LUTdq
        a LUTdq object

    """

    raise AbstractClassError(
        "EEC is an abstract class, please create one of its daughters."
    )
