from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def convert_to_P(self, other_dict: dict, machine: Machine, other_unit_dict: dict):
    """Selects value in other_dict and implements it in machine

    Parameters
    ----------
    self : RulesComplex
        A RuleComplex object
    other_dict : dict
        dict created from the file to be converted
    machine : Machine
        A pyleecan machine
    other_unit_dict : dict
        dict with unit to make conversion (key: unit family, value: factor)
    """
    # Local import (circular: the registry imports the rule modules)
    from ....Functions_new.Converter.rule_functions import rule_function_module

    machine = rule_function_module(self.fct_name).other_to_P(
        self, machine, other_dict, other_unit_dict
    )

    return machine
