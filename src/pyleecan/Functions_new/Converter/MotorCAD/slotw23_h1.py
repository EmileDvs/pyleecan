from typing import TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict | None = None
):
    """Conversion H1 in m to slotW11

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
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
    warn(
        "other_to_P is deprecated, it is not used by the MotorCAD conversion rules (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    H1 = machine.stator.slot.get_H1()

    machine.stator.slot.H1 = H1
    machine.stator.slot.H1_is_rad = False
    return machine


def P_to_other(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict | None = None
) -> dict:
    """conversion obj machine in dict

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
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
    warn(
        "P_to_other is deprecated, it is not used by the MotorCAD conversion rules (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return other_dict
