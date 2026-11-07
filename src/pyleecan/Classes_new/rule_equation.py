# Experimental dataclass generated from Generator/ClassesRef/Converter/RuleEquation.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from sympy.solvers import solve

from .rule import Rule


@dataclass(eq=False)
class RuleEquation(Rule):
    """simple rules

    Attributes
    ----------
    param : list or None
        dict all parameters
        Default: []
    equation : str or None
        conversion paramter to pyleecan (Y are always on other side
        Default: None
    file_name : str or None
        use just to debug, give name of file
        Default: None
    """

    param: list[Any] | None = field(default_factory=list)
    """dict all parameters"""
    equation: str | None = None
    """conversion paramter to pyleecan (Y are always on other side"""
    file_name: str | None = None
    """use just to debug, give name of file"""

    # Inlined from Methods.Converter.RuleEquation.convert_to_other
    def convert_to_other(self, other_dict, machine, other_unit_dict):
        """Selects value in machine and implements it in other_dict

        Parameters
        ----------
        self : RuleEquation
            A RuleEquation object
        other_dict : dict
            dict created from the machine to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """

        value = self.solve_equation(
            other_dict, machine, other_unit_dict, is_P_to_other=False
        )

        # adding value in other_dict
        for variable in self.param:
            if variable["variable"] == "y":
                list_path = variable["path"]
                other_dict = self.set_other(
                    other_dict, value, other_unit_dict, list_path
                )

        return other_dict

    # Inlined from Methods.Converter.RuleEquation.convert_to_P
    def convert_to_P(self, other_dict, machine, other_unit_dict):
        """Selects value in other_dict and implements it in machine

        Parameters
        ----------
        self : RulesEquation
            A RuleEquation object
        other_dict : dict
            dict created from the file to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)

        """

        value = self.solve_equation(
            other_dict, machine, other_unit_dict, is_P_to_other=True
        )

        for param in self.param:
            if param["variable"] == "x":
                self.set_P(machine, value, param["path"])

        return machine

    # Inlined from Methods.Converter.RuleEquation.solve_equation
    def solve_equation(self, other_dict, machine, other_unit_dict, is_P_to_other):
        if is_P_to_other:
            name_var = "x"
        else:
            name_var = "y"

        # we must have the same unit for all parameters used in equation
        equation = self.equation

        for param in self.param:
            if param["src"] == "other":
                if (
                    param["src"] == "other"
                    and not param["variable"].lower() == name_var
                ):
                    other_value = self.get_other(
                        other_dict, param["path"], other_unit_dict
                    )
                    equation = equation.replace(param["variable"], str(other_value))

        for param in self.param:
            if param["src"] == "pyleecan":
                if not param["variable"] == name_var:
                    P_value = self.get_P(param["path"], machine)
                    equation = equation.replace(param["variable"], str(P_value))

        # equation cleaning, delete space and replace + and - to delete =
        equation = equation.replace(" ", "")
        equation = equation.split("=")

        equation = equation[0] + "-(" + equation[1] + ")"

        value = solve(equation)
        # value return a list of equation, all equations are first order so have only one solution
        return float(value[0])
