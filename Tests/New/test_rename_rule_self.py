"""rename_rule_self: first parameter of the complex rule functions named `rule` (Step 15)."""

import ast

from pyleecan.Generator.ClassGenerator.New.function_module_names import rename_rule_self

SOURCE = '''def other_to_P(self, machine, other_dict, other_unit_dict=None):
    """Converts

    Parameters
    ----------
    self : ConvertMC
        A ConvertMC object
    machine : Machine
        A pyleecan machine
    """
    self.unit_type = "m"
    value = self.get_other(other_dict, ["a"], other_unit_dict)
    label = f"{self.unit_type}"
    return machine


def helper(machine):
    self = machine  # not a rule function: unchanged
    return self
'''


def test_rule_parameter_renamed_with_its_uses():
    result = rename_rule_self(SOURCE)
    function = ast.parse(result).body[0]
    assert [arg.arg for arg in function.args.args][0] == "rule"
    names = {node.id for node in ast.walk(function) if isinstance(node, ast.Name)}
    assert "self" not in names and "rule" in names
    assert 'rule.unit_type = "m"' in result
    assert 'f"{rule.unit_type}"' in result
    assert "    rule : RuleComplex\n        The complex conversion rule\n" in result
    assert "ConvertMC" not in result


def test_other_functions_unchanged_and_idempotent():
    result = rename_rule_self(SOURCE)
    assert "    self = machine  # not a rule function: unchanged\n    return self\n" in result
    assert rename_rule_self(result) == result
