from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.converter.rule_complex import RuleComplex
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    rule: RuleComplex,
    machine: Machine,
    other_dict: dict,
    other_unit_dict: dict | None = None,
):
    """Conversion H1 in m to slotW11

    Parameters
    ----------
    rule : RuleComplex
        The complex conversion rule
    machine : Machine
        A obj machine
    other_dict : dict
        A dict with the conversion obj machine
    other_unit_dict : dict
        dict with unit to make conversion (key: unit family, value: factor)

    Return
    ---------
    machine : Machine
        A obj machine
    """
    H1 = machine.stator.slot.get_H1()

    machine.stator.slot.H1 = H1
    machine.stator.slot.H1_is_rad = False
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
