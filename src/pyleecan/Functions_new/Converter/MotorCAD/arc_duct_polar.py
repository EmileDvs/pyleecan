from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ....Classes_new.converter.rule_complex import RuleComplex
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    rule: RuleComplex, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Conversion of the slot arc duct (motor-cad) into polar duct (pyleecan)

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

    if isinstance(rule.param_dict["duct_id"], int):
        duct_id = rule.param_dict["duct_id"]
    else:
        ValueError("duct_id isn't int")

    lam_name_MC = rule.param_dict["lam_name_MC"]
    lam_name_py = rule.param_dict["lam_name_py"]

    other_path_list = [
        "[Through_Vent]",
        f"{lam_name_MC}CircularDuctLayer_Channels[{duct_id}]",
    ]
    rule.unit_type = ""
    Zh = rule.get_other(other_dict, other_path_list, other_unit_dict)
    gamma = 2 * np.pi / Zh

    rule.unit_type = "m"
    other_path_list = [
        "[Through_Vent]",
        f"{lam_name_MC}ArcDuctLayer_InnerDiameter[{duct_id}]",
    ]
    H0 = rule.get_other(other_dict, other_path_list, other_unit_dict)
    H0 = H0 * 0.5

    rule.unit_type = "m"
    other_path_list = [
        "[Through_Vent]",
        f"{lam_name_MC}ArcDuctLayer_WebWidth[{duct_id}]",
    ]
    A = rule.get_other(other_dict, other_path_list, other_unit_dict)

    other_value = gamma - (np.pi / 180) * np.arccos((2 * H0 * H0 - A * A) / (2 * H0))

    path = f"machine.{lam_name_py}.axial_vent[{duct_id}].W1"
    rule.set_P(machine, other_value, path)
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
