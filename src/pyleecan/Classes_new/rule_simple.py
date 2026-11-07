# Experimental dataclass generated from Generator/ClassesRef/Converter/RuleSimple.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from .rule import Rule


@dataclass(eq=False)
class RuleSimple(Rule):
    """simple rules

    Attributes
    ----------
    other_key_list : list or None
        parameter
        Default: []
    P_obj_path : str or None
        path pyleecan parameter in object machine
        Default: None
    scaling_to_P : float
        conversion paramter to pyleecan
        Default: 1
    file_name : str or None
        use just to debug, give name of file
        Default: None
    """

    other_key_list: list[Any] | None = field(default_factory=list)
    """parameter """
    P_obj_path: str | None = None
    """path pyleecan parameter in object machine """
    scaling_to_P: float = 1
    """conversion paramter to pyleecan"""
    file_name: str | None = None
    """use just to debug, give name of file"""

    # Inlined from Methods.Converter.RuleSimple.convert_to_other
    def convert_to_other(self, other_dict, machine, other_unit_dict):
        """Selects value in machine and implements it in other_dict

        Parameters
        ----------
        self : RuleSimple
            A RuleSimple object
        other_dict : dict
            dict created from the file to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """

        P_value = self.get_P(self.P_obj_path, machine)

        # possibility to have str in other_value, if other_value is a str we have an equivalent, and we can't multiply a str.
        # The "if" here handles this issue
        if self.scaling_to_P != 1:
            P_value = P_value / self.scaling_to_P

        # set value in other_dict
        other_dict = self.set_other(
            other_dict, P_value, other_unit_dict, self.other_key_list
        )

        return other_dict

    # Inlined from Methods.Converter.RuleSimple.convert_to_P
    def convert_to_P(self, other_dict, machine, other_unit_dict):
        """Selects value in other_dict and implements it in machine

        Parameters
        ----------
        self : RuleSimple
            A RuleSimple object
        other_dict : dict
            dict created from the file to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """

        # select correct value
        # The value is return in pyleecan unit (SI)
        other_value = self.get_other(other_dict, self.other_key_list, other_unit_dict)

        # possibility to have str in other_value, if other_value is a str we have an equivalent, and we can't multiply a str.
        # The "if" here handles this issue
        if self.scaling_to_P != 1:
            other_value = other_value * self.scaling_to_P

        machine = self.set_P(machine, other_value, self.P_obj_path)

        return machine
