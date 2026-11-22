from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def get_Jrms(self, output: Output | None = None) -> float:
    """Return the stator current density rms value

    Parameters
    ----------
    self : OutElec
        an OutElec object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)

    Returns
    -------
    Jrms: float
        stator current density rms value [A/m^2]
    """
    output = container_or_parent(self, output, "output")

    if self.Jrms is None:
        machine = output.simu.machine

        Swire = machine.stator.winding.conductor.comp_surface_active()
        Npcp = machine.stator.winding.Npcp

        Idq_dict = self.OP.get_Id_Iq()

        self.Jrms = np.sqrt(Idq_dict["Id"] ** 2 + Idq_dict["Iq"] ** 2) / (Swire * Npcp)

    return self.Jrms
