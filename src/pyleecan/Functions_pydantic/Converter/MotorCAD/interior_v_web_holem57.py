from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ....Classes_pydantic.converter.rule_complex import RuleComplex
    from ....Classes_pydantic.machine.machine import Machine


def other_to_P(
    rule: RuleComplex, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Converts interior_V_webe motor-cad slot into pyleecan holeM57
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

    # selection hole_id
    if isinstance(rule.param_dict["hole_id"], int):
        hole_id = rule.param_dict["hole_id"]
    else:
        ValueError("hole_id isn't int")

    rule.unit_type = "m"
    other_path_list = ["[Dimensions]", f"MagnetSeparation_Array[{hole_id}]"]
    W = rule.get_other(other_dict, other_path_list, other_unit_dict)

    point_dict = machine.rotor.hole[hole_id]._comp_point_coordinate()
    Z9 = point_dict["Z9"]
    Z4 = point_dict["Z4"]

    # In Pyleecan to place magnet, W2 is set on top of the slot, contrary to MC equivalent at W2 is set at the bottom
    # Set W2
    machine.rotor.hole[hole_id].W2 = (
        abs(Z9 - Z4)
        - machine.rotor.hole[hole_id].W4
        - (
            ((W - machine.rotor.hole[hole_id].W1) / 2)
            / np.sin(machine.rotor.hole[hole_id].W0 / 2)
        )
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
