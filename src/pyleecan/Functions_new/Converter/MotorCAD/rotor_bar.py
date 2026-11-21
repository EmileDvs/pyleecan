from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def other_to_P(
    self, machine: Machine, other_dict: dict, other_unit_dict: dict
) -> Machine:
    """Converts motor-cad into pyleecan for rotor bar

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
    self.unit_type = "m"
    other_path_list = ["[Dimensions]", "EndRing_Inner_Add_F"]
    H0 = self.get_other(other_dict, other_path_list, other_unit_dict)

    self.unit_type = "m"
    other_path_list = ["[Dimensions]", "EndRing_Outer_Add_F"]
    H1 = self.get_other(other_dict, other_path_list, other_unit_dict)

    H = machine.rotor.slot.comp_height()

    self.unit_type = "m"
    other_path_list = ["[Dimensions]", "EndRing_Thickness_F"]
    W0 = self.get_other(other_dict, other_path_list, other_unit_dict)

    self.unit_type = "m"
    other_path_list = ["[Dimensions]", "EndRing_Thickness_R"]
    W1 = self.get_other(other_dict, other_path_list, other_unit_dict)

    machine.rotor.Lscr = (W1 + W0) / 2
    machine.rotor.Hscr = H + H0 + H1
    machine.rotor.winding.Lewout = 0
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

    return other_dict
