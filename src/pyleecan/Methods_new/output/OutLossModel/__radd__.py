from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.out_loss_model import OutLossModel


def __radd__(self, other: OutLossModel | dict | int) -> OutLossModel:
    """Add two loss models output (called for: other + self)

    Parameters
    ----------
    self : OutLossModel
        First loss model to add
    other : OutLossModel or dict or int
        Second loss model to add
        (0: the start value of sum(), self is returned)

    Returns
    -------
    loss_tot : OutLossModel
        Resulting Losses output
    """
    if isinstance(other, int):  # Start value of sum()
        if other == 0:
            return self
        raise TypeError(f"Cannot combine an OutLossModel with {other!r}")
    if isinstance(other, dict):  # Dump of an OutLossModel
        other_loss_density = other["loss_density"]
        other_coeff_dict = other["coeff_dict"]
        other_name = other["name"]
        other_group = other["group"]
    else:
        other_loss_density = other.loss_density
        other_coeff_dict = other.coeff_dict
        other_group = other.group
        other_name = other.name

    new_loss_density = self.loss_density + other_loss_density
    new_coeff_dict = self.coeff_dict.copy()
    for key, value in other_coeff_dict.items():
        if key in new_coeff_dict:
            new_coeff_dict[key] += value
        else:
            new_coeff_dict[key] = value
    new_group = self.group + " + " + other_group
    new_name = self.name + " + " + other_name
    return OutLossModel(
        name=new_name,
        loss_density=new_loss_density,
        coeff_dict=new_coeff_dict,
        group=new_group,
    )
