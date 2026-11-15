import pytest
from numpy import pi
from backend_classes.machine.winding import Winding
from backend_classes.converter.rule_complex import RuleComplex
from backend_classes.machine.machine_sipmsm import MachineSIPMSM
from backend_classes.machine.lam_slot_wind import LamSlotWind
from backend_classes.machine.end_winding import EndWinding


winding_test = list()

# Common values
other_dict = {
    "[Winding_Design]": {
        "EWdg_MLT": 950,
    }
}

winding_test.append(
    {
        "other_dict": other_dict,
        "Lewout": 0.0625 / 1000,
    }
)

# Common values
other_dict = {
    "[Winding_Design]": {
        "EWdg_MLT": 1523,
    }
}

winding_test.append(
    {
        "other_dict": other_dict,
        "Lewout": 0.20575 / 1000,
    }
)


class TestComplexRuleEndWindingLenght(object):
    @pytest.mark.parametrize("test_dict", winding_test)
    def test_end_winding_lenght(self, test_dict):
        """test rule complex"""

        # retreive other_dict
        other_dict = test_dict["other_dict"]

        machine = MachineSIPMSM()
        machine.stator = LamSlotWind()
        machine.stator.winding = Winding()
        machine.stator.winding.end_winding = EndWinding()
        machine.stator.Rext = 0.5
        machine.stator.Rint = 0.35

        # Define and apply the slot rule
        rule = RuleComplex(fct_name="end_winding_lenght", folder="MotorCAD")
        # first rule complex use to define a slot
        machine = rule.convert_to_P(
            other_dict, machine, {"ED": (2 / 8) * (pi / 180), "m": 0.001, "": 1}
        )

        # retreive expected value
        Lewout = test_dict["Lewout"]

        # check the convertion
        msg = f"{machine.stator.winding.Lewout} expected {Lewout}"
        assert machine.stator.winding.Lewout == pytest.approx(Lewout), msg


if __name__ == "__main__":
    a = TestComplexRuleEndWindingLenght()
    for test_dict in winding_test:
        a.test_end_winding_lenght(test_dict)
    print("Test Done")
