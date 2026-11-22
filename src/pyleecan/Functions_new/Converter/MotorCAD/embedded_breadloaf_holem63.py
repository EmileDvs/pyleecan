from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ....Classes_new.converter.rule_complex import RuleComplex
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    rule: RuleComplex, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Conversion of the slot inset_breadloaf (motor-cad) into the slotM12 (pyleecan)

    Parameters
    ----------
    rule : RuleComplex
        The complex conversion rule
    machine : Machine
        A pyleecan machine
    other_dict : dict
        A dict with the conversion obj machine
    other_unit_dict : dict
        dict with unit to make conversion (key: unit family, value: factor)

    Returns
    ---------
    machine : Machine
        A pyleecan machine
    """
    if isinstance(rule.param_dict["hole_id"], int):
        hole_id = rule.param_dict["hole_id"]
    else:
        ValueError("hole_id isn't int")

    rule.unit_type = "m"
    other_path_list = ["[Dimensions]", "Magnet_Embed_Depth"]
    H1 = rule.get_other(other_dict, other_path_list, other_unit_dict)
    Rbo = machine.rotor.get_Rbo()

    H = Rbo - H1
    rule.unit_type = "ED"
    other_path_list = ["[Dimensions]", "Magnet_Arc_[ED]"]
    W0 = rule.get_other(other_dict, other_path_list, other_unit_dict)

    Rbo = machine.rotor.get_Rbo()

    W0 = H * np.tan(W0 / 2)

    machine.rotor.hole[hole_id].W0 = W0 * 2

    return machine


def P_to_other(
    rule: RuleComplex,
    machine: Machine,
    other_dict: dict,
    other_unit_dict: dict | None = None,
) -> dict:
    """conversion obj machine in dict

    Parameters
    ----------
    rule : RuleComplex
        The complex conversion rule
    machine : Machine
        A pyleecan machine
    other_dict : dict
        A dict with the conversion obj machine
    other_unit_dict : dict
        dict with unit to make conversion (key: unit family, value: factor)

    Returns
    ---------
    other_dict : dict
        A dict with the conversion obj machine
    """

    return other_dict
