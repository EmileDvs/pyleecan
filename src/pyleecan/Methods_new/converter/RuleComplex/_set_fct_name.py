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

    # The rule functions are found from the name when the rule runs
    # (convert_to_P / convert_to_other call rule_function_module): the legacy
    # other_to_P / P_to_other attributes are not set
    self._fct_name = value
