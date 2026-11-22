from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def comp_power(self, output: Output | None = None) -> None:
    """Compute the Ouput power

    Parameters
    ----------
    self : OutMag
        An OutMag object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)
    """
    output = container_or_parent(self, output, "output")

    if (
        output is not None
        and output.elec is not None
        and output.elec.OP.get_N0() is not None
        and self.Tem_av is not None
    ):
        self.Pem_av = 2 * np.pi * output.elec.OP.get_N0() / 60 * self.Tem_av
    else:
        self.Pem_av = None
