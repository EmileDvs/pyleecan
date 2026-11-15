from ....classes_common.check import check_var


def _set_fct_name(self, value):
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
        module = __import__(
            f"pyleecan.Functions_new.Converter.MotorCAD.{('curve_bh' if self.fct_name == 'curve_B(H)' else self.fct_name.lower().replace('(', '_').replace(')', ''))}",
            fromlist=(self.fct_name),
        )
        self.other_to_P = getattr(module, "other_to_P")
        self.P_to_other = getattr(module, "P_to_other")
