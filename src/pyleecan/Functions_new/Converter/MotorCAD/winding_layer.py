from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict | None = None
) -> Machine:
    """Conversion of winding

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
    self.unit_type = ""
    other_path_list = ["[Winding_Design]", "Winding_Type"]
    Nlayer = self.get_other(other_dict, other_path_list, other_unit_dict)

    self.unit_type = ""
    other_path_list = ["[Magnetics]", "MagPathType"]
    type = self.get_other(other_dict, other_path_list, other_unit_dict)

    if Nlayer == "Overlapping":
        machine.stator.winding.Nlayer = 2
        if type == 2:
            machine.stator.winding.is_change_layer = True
        else:
            machine.stator.winding.is_change_layer = False

    else:
        machine.stator.winding.Nlayer = 1
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

    pass
