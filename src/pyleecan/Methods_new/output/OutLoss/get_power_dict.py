from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def get_power_dict(self, output: Output | None = None) -> dict[str, float]:
    """Return a dictionnary with all the scalar losses

    Parameters
    ----------
    self : OutLoss
        An OutLoss object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)

    Returns
    -------
    power_dict : {float}
        Dictionnary of all the scalar losses
    """
    output = container_or_parent(self, output, "output")

    if output is None:
        raise Exception("Error: OutLoss is not in Output object")
    out = output
    if out.elec is None or out.elec.OP is None:
        raise Exception("Error: OP is not set")

    power_dict = dict(
        [
            (o.name, o.get_loss_scalar(out.elec.OP.felec))
            for o in self.loss_dict.values()
        ]
    )

    if out.mag is not None and out.mag.Pem_av is not None:
        power_dict["total_power"] = out.mag.Pem_av

    return power_dict
