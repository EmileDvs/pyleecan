"""Check that ClassInfo rebuilds the class information from the dataclasses."""

import pytest

from backend_classes._class_info import PYLEECAN_BASES, ClassInfo
from pyleecan.definitions import DOC_DIR
from pyleecan.classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _property_description,
    _property_metadata,
)
from pyleecan.Generator.read_fct import read_all

class_dict = ClassInfo().get_dict()
# Transitional reference: the CSV files the dataclasses were generated from
gen_dict = read_all(DOC_DIR)


def _new_name(name):
    return NORMALIZATION_CLASS_NAMES.get(name, name)


def test_same_classes_as_csv():
    assert set(class_dict) == {_new_name(name) for name in gen_dict}


@pytest.mark.parametrize("csv_dict", list(gen_dict.values()), ids=lambda c: c["name"])
def test_class_info_matches_csv(csv_dict):
    info = class_dict[_new_name(csv_dict["name"])]

    assert info["mother"] == _new_name(csv_dict["mother"])
    assert info["package"] == csv_dict["package"]
    assert info["daughters"] == sorted(_new_name(n) for n in csv_dict["daughters"])
    assert issubclass(info["class"], PYLEECAN_BASES)
    # Every CSV method is a method of the dataclass (inlined helpers may be added)
    assert {m.split(".")[-1] for m in csv_dict["methods"]} <= set(info["methods"])
    # Own properties come first, in CSV order with the "_" ones at the end
    csv_names = [prop["name"] for prop in csv_dict["properties"]]
    own_names = [name for name in csv_names if not name.startswith("_")] + [
        name for name in csv_names if name.startswith("_")
    ]
    assert [p["name"] for p in info["properties"][: len(own_names)]] == own_names
    for prop in csv_dict["properties"]:
        result = info["prop_dict"][prop["name"]]
        expected = _property_metadata(prop)
        assert result["desc"] == _property_description(prop)
        assert result["unit"] == expected.get("unit", "")
        assert result["min"] == expected.get("min")
        assert result["max"] == expected.get("max")


def test_inherited_properties_and_mothers():
    info = ClassInfo()
    assert info.get_mothers("Arc1") == ["Arc", "Line"]
    assert {"begin", "end", "radius", "prop_dict"} <= set(
        info.get_dict()["Arc1"]["prop_dict"]
    )
    assert "Line" in info.get_base_classes()


def test_prop_types():
    lam = class_dict["LamSlotWind"]["prop_dict"]
    assert lam["Ksfill"]["type"] == "float"
    assert (lam["Ksfill"]["min"], lam["Ksfill"]["max"]) == (0, 1)
    assert lam["winding"]["type"] == "Winding"
    assert class_dict["SurfLine"]["prop_dict"]["line_list"]["type"] == "[Line]"


def test_empty_metadata_is_not_generated():
    prop = {"name": "x", "type": "float", "value": 0, "desc": "", "unit": ""}
    prop.update({"min": "", "max": "", "as_dict": "", "size": ""})
    assert _property_metadata(prop) == {}
    prop.update({"desc": "Not stored", "unit": "-"})
    assert _property_metadata(prop) == {}
    prop.update({"unit": "m", "min": "0", "max": "6.29"})
    assert _property_metadata(prop) == {"unit": "m", "min": 0, "max": 6.29}
