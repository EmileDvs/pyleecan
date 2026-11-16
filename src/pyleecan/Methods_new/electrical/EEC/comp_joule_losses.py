from . import AbstractClassError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_joule_losses(self, out_dict: dict, machine: Machine) -> dict:
    """Compute the electrical Joule losses

    Parameters
    ----------
    self : EEC
        an EEC object
    out_dict : dict
        Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
    machine : Machine
        a Machine object

    Returns
    ------
    out_dict : dict
        Dict containing all magnetic quantities that have been calculated in EEC
    """

    raise AbstractClassError(
        "EEC is an abstract class, please create one of its daughters."
    )
