# Experimental dataclass generated from Generator/ClassesRef/Converter/Rule.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Rule(PyleecanClass):
    """abstract class for rules

    Attributes
    ----------
    unit_type : str
        unit
        Default: "m"
    """

    unit_type: str = "m"
    """unit"""

    def __post_init__(self):
        super().__post_init__()

    # Inlined from Methods.Converter.Rule.get_name
    def get_name(self):
        """Return the name of file or function

        Parameters
        ----------
        self : Rule
            A Rule object
        """
        if self.__class__.__name__ == "RuleComplex":
            return self.fct_name
        else:
            return self.file_name

    # Inlined from Methods.Converter.Rule.get_other
    def get_other(self, other_dict, other_path_list, other_unit_dict):
        """Select value in other_dict and change the value to be in SI

        Parameters
        ----------
        self : Rule
            A Rule object
        other_dict : dict
            dict with all other param
        other_path_list : list
            list with path to set value ( ["[Dimensions]", "Pole_Arc"])
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)

        Return
        ----------
        other_value
        """

        unit = other_unit_dict[self.unit_type]

        try:
            # selection correct value in other_dict
            for temp in other_path_list:
                other_dict = other_dict[temp]
        except AttributeError:
            raise ValueError(
                f"Value equivalent at {other_path_list} isn't found in other_dict"
            )

        other_value = other_dict * unit

        return other_value  # return in SI

    # Inlined from Methods.Converter.Rule.get_P
    def get_P(self, path_machine, machine):
        """Select value in machine

        Parameters
        ----------
        self : Rule
            A Rule object
        machine : Machine
            A obj machine
        path_machine : str
            str with the path in obj machine

        Return
        ----------
        P_value
        """
        # select value in object machine
        value_split = path_machine.split(".")

        path = ".".join(value_split[:-1])
        # value_split[-1] is the attribut that we want to retrieve ("W1")
        # path is the attribut chain to get the attribut ("machine.stator.slot")

        try:
            P_value = getattr(
                eval(path),
                value_split[-1],
            )
        except AttributeError:
            raise ValueError(
                f"Value equivalent at {path_machine} isn't found in obj machine"
            )

        return P_value

    # Inlined from Methods.Converter.Rule.set_other
    def set_other(self, other_dict, P_value, other_unit_dict, path_list):
        """Set P_value value in other_dict

        Parameters
        ----------
        self : Rule
            A Rule object
        other_dict : dict
            dict created from the file to be converted
        P_value :
            value to set in other_dict
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        path_list : list
            list with path to set the value


        Return
        ----------
        other_dict
        """
        unit = other_unit_dict[self.unit_type]

        P_value = P_value / unit  # set in correct unit

        # Make sure that all the sub-keys exist
        dict_temp = other_dict
        for key in path_list[:-1]:
            if key not in dict_temp:
                dict_temp[key] = {}
            dict_temp = dict_temp[key]

        # Set the value
        last_key = path_list[-1]
        dict_temp[last_key] = P_value

        return other_dict

    # Inlined from Methods.Converter.Rule.set_P
    def set_P(self, machine, other_value, path):
        """Set value in machine

        Parameters
        ----------
        self : Rule
            A Rule object
        machine : Machine
            A pyleecan machine
        other_value :
            value to set in other_dict
        path : str
            path to set the value


        Return
        ----------
        machine
        """
        # set value in object machine
        value_split = path.split(".")

        # value_split[-1] is the attribut that we want to set ("W1")
        # path is the attribut chain to set the attribut ("machine.stator.slot")
        path = ".".join(value_split[:-1])

        setattr(
            eval(path),
            value_split[-1],
            other_value,
        )
        return machine
