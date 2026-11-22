from ....classes_common.errors import NotImplementedYetError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def comp_force_nodal(self, output: Output):
    """Compute the nodal air-gap surface force based on Maxwell Tensor (MT).

    Parameters
    ----------
    self : ForceMT
        A ForceMT object

    output : Output
        an Output object (to update)
    """

    raise NotImplementedYetError("Nodal force not available yet for Maxwell tensor")
