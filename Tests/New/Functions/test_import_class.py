"""Tests for dynamic class imports."""

import pytest

from pyleecan.classes_common.check import InitUnKnowClassError
from backend_classes.magnetics.magnetics import Magnetics
from backend_functions.Load.import_class import import_class


def test_import_class_returns_class():
    assert import_class("pyleecan.Classes", "Magnetics") is Magnetics


@pytest.mark.parametrize(
    ("prop_name", "message"),
    [
        ("", "Unknow class name MissingClass when loading"),
        ("mag", "Unknow class name MissingClass in init_dict for property mag"),
    ],
)
def test_import_class_reports_unknown_class(prop_name, message):
    with pytest.raises(InitUnKnowClassError, match=message):
        import_class("pyleecan.Classes", "MissingClass", prop_name)


def test_import_class_reports_missing_attribute(tmp_path, monkeypatch):
    package = tmp_path / "test_import_package"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "MissingClass.py").write_text("value = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(InitUnKnowClassError, match="MissingClass when loading"):
        import_class("test_import_package", "MissingClass")
