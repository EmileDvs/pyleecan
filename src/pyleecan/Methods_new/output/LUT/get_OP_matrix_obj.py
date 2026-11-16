from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.simulation.op_matrix import OPMatrix


def get_OP_matrix_obj(self) -> OPMatrix | None:
    """Get the Operating Point Matrix

    Parameters
    ----------
    self : LUT
        a LUT object

    Returns
    ----------
    OP_matrix : OPMatrix
        Operating Point Matrix object
    """

    if self.simu is None:
        return None
    var_load = self.simu.get_var_load()
    if var_load is None:
        return None
    return var_load.OP_matrix
