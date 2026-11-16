from .....Classes_new.converter.rule_complex import RuleComplex


def add_rule_skew(self) -> None:
    """Create and adapt all the rules related to skew
    Extend rules_list within Converter object

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
    """

    self.rules_list.append(
        RuleComplex(
            fct_name="skew",
            folder="MotorCAD",
        )
    )
