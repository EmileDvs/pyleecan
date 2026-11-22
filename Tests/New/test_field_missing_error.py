"""FieldMissingError: shared error of the methods using a field that defaults to None (Step 14)."""

import ast

import pytest

from pyleecan.Generator.ClassGenerator.New import class_generator


def test_field_missing_error_is_written_with_the_shared_errors(tmp_path):
    class_dir = tmp_path / "Classes_new"
    class_dir.mkdir()
    (tmp_path / class_generator.COMMON_PACKAGE).mkdir()
    class_generator._write_shared_errors(str(class_dir), {})
    error_path = tmp_path / class_generator.COMMON_PACKAGE / "errors.py"
    tree = ast.parse(error_path.read_text(encoding="utf-8"))
    generated = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    assert [base.id for base in generated["FieldMissingError"].bases] == ["Exception"]
    assert "FieldMissingError" in class_generator.CLASS_ERROR_NAMES


def test_field_missing_error_raised_by_a_method():
    from pyleecan.classes_common.errors import FieldMissingError
    from pyleecan.Classes_new.force.force_mt import ForceMT
    from pyleecan.Classes_new.output.output import Output

    output = Output()
    assert output.force.AGSF is None
    with pytest.raises(FieldMissingError, match="OutForce.AGSF is None"):
        ForceMT(Rsbo_enforced_transfer=0.1).comp_AGSF_transfer(output)
