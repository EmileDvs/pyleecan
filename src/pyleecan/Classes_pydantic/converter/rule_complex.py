# Experimental pydantic model generated from Generator/ClassesRef/Converter/RuleComplex.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import Field

from ...classes_common.check import check_var
from .rule import Rule

if TYPE_CHECKING:
    from ..machine.machine import Machine


class RuleComplex(Rule):
    """complex rules

    Attributes
    ----------
    fct_name : str or None
        fonction name to convert
        Default: None
    folder : str or None
        name source
        Default: None
    param_dict : dict
        dict to pass param
        Default: -1
    """

    fct_name: str | None = None
    """fonction name to convert"""
    folder: str | None = None
    """name source"""
    param_dict: dict[str, Any] = Field(default_factory=dict)
    """dict to pass param """

    _package: ClassVar[str] = "Converter"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Converter.RuleComplex._set_fct_name
    def _set_fct_name(self, value: str) -> None:
        """find the path of a function

        Parameters
        ----------
        self : RuleComplex
            A RuleComplex object
        value : str
            name of file for complex rule

        """

        # Check that value is a str
        check_var("_fct_name", value, "str")

        self._fct_name = value

        # Load the function
        if self._fct_name is not None:
            # Local import (circular: the registry imports the rule modules)
            from ...Functions_pydantic.Converter.rule_functions import (
                rule_function_module,
            )

            module = rule_function_module(self.fct_name)
            self.other_to_P = getattr(module, "other_to_P")
            self.P_to_other = getattr(module, "P_to_other")

    # Inlined from Methods.Converter.RuleComplex.convert_to_other
    def convert_to_other(
        self, other_dict: dict, machine: Machine, other_unit_dict: dict
    ):
        """Selects value in machine and implements it in other_dict

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
        from ...Functions_pydantic.Converter.rule_functions import rule_function_module

        other_dict = rule_function_module(self.fct_name).P_to_other(
            self, machine, other_dict
        )

        return other_dict

    # Inlined from Methods.Converter.RuleComplex.convert_to_P
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
        from ...Functions_pydantic.Converter.rule_functions import rule_function_module

        machine = rule_function_module(self.fct_name).other_to_P(
            self, machine, other_dict, other_unit_dict
        )

        return machine
