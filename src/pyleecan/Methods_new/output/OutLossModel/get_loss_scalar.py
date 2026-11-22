from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.out_loss import OutLoss
    from ....Classes_new.output.output import Output


def get_loss_scalar(self, felec: float | None = None, out_loss: OutLoss | None = None, output: Output | None = None) -> float:
    """Get loss power from coefficients stored in coeff_dict

    Parameters
    ----------
    self : OutLossModel
        an OutLossModel object
    felec : float
        the electrical frequency [Hz]
    out_loss : OutLoss, optional
        OutLoss holding the model (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the OutLoss)

    Returns
    -------
    Ploss : float
        loss power for the specified frequency [W]
    """
    output = container_or_parent(self, output, "output", depth=2)

    if self.coeff_dict is None:
        return self.scalar_value  # Can be None
    else:
        if felec is None:
            felec = output.elec.OP.felec
        Ploss = 0
        for key, value in self.coeff_dict.items():
            Ploss += value * felec ** float(key)
        self.scalar_value = Ploss
    return self.scalar_value
