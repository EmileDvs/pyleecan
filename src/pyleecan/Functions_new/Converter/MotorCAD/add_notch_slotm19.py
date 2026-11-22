from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ....Classes_new.converter.rule_complex import RuleComplex
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    rule: RuleComplex, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Converts motor-cad notch into pyleecan notch slotM19

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
    rule.unit_type = "m"
    other_path_list = ["[Dimensions]", "PoleNotchDepth"]
    H0 = rule.get_other(other_dict, other_path_list, other_unit_dict)
    Rbo = machine.rotor.get_Rbo()

    rule.unit_type = "ED"
    other_path_list = ["[Dimensions]", "PoleNotchArc_Outer"]
    W1 = rule.get_other(other_dict, other_path_list, other_unit_dict)

    rule.unit_type = "ED"
    other_path_list = ["[Dimensions]", "PoleNotchArc_Inner"]
    W0 = rule.get_other(other_dict, other_path_list, other_unit_dict)

    machine.rotor.notch[0].notch_shape.W1 = np.sqrt(2 * Rbo**2 * (1 - np.cos(W1)))
    machine.rotor.notch[0].notch_shape.W0 = np.sqrt(
        2 * (Rbo - H0) ** 2 * (1 - np.cos(W0))
    )

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
