from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def comp_emf(self, output: Output | None = None) -> None:
    """Compute the Electromotive force [V]

    Parameters
    ----------
    self : OutMag
        an OutMag object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)

    """
    output = container_or_parent(self, output, "output")

    # Get stator winding flux
    Phi_wind = self.Phi_wind[output.simu.machine.stator.get_label()]

    EMF = Phi_wind.get_data_along("time=derivate", "phase")

    EMF.name = "Stator Winding Electromotive Force"
    EMF.unit = "V"
    EMF.symbol = "EMF"

    self.emf = EMF
