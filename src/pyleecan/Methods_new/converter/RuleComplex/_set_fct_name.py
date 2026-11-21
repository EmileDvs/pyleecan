from ....classes_common.check import check_var


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
        from ....Functions_new.Converter.rule_functions import rule_function_module

        module = rule_function_module(self.fct_name)
        self.other_to_P = getattr(module, "other_to_P")
        self.P_to_other = getattr(module, "P_to_other")
