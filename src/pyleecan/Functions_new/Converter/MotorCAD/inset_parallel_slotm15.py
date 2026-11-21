from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Converts motor-cad inset_parallel slot into pyleecan slotM15
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
    machine : Machine
        A pyleecan machine
    """
    Rbo = machine.rotor.get_Rbo()

    self.unit_type = "ED"
    other_path_list = ["[Dimensions]", "Magnet_Arc_[ED]"]
    W1 = self.get_other(other_dict, other_path_list, other_unit_dict)

    # In Pyleecan W1[m] and W0[rad]
    # In MC W1 = W0 [ED]

    # Set W1
    slot_width = (Rbo) * np.sin(W1 / 2)
    machine.rotor.slot.W1 = 2 * slot_width

    # Set Rtopm
    machine.rotor.slot.Rtopm = Rbo

    point_dict = machine.rotor.slot._comp_point_coordinate()
    ZM4 = point_dict["ZM4"]

    # set W0
    machine.rotor.slot.W0 = 2 * np.arcsin((machine.rotor.slot.W1 / 2) / abs(ZM4))

    return machine


def P_to_other(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict | None = None
) -> dict:
    """conversion obj machine into dict

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

    return other_dict
