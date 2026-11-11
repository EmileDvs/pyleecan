import pytest

from pyleecan.Functions_new.Load.retrocompatibility import (
    convert_init_dict,
    convert_normalization,
    create_update_dict,
)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("Norm_ref", "NormRef"),
        ("Norm_affine", "NormAffine"),
        ("Norm_func", "NormFunc"),
        ("Norm_indices", "NormIndices"),
        ("Norm_vector", "NormVector"),
    ],
)
def test_convert_normalization_in_place(old, new):
    data = {"__class__": old, "value": 42}
    convert_normalization(data)
    assert data == {"__class__": new, "value": 42}
    convert_normalization(data)
    assert data == {"__class__": new, "value": 42}


@pytest.mark.parametrize(
    ("version", "expected"),
    [(None, True), ("1.5.1", True), ("1.5.2", False), ("1.6.0", False)],
)
def test_normalization_conversion_version_gate(version, expected):
    assert create_update_dict(version)["Normalization"] is expected
    normalization = {"__class__": "Norm_vector", "vector": [1, 2]}
    data = {"__class__": "Data", "normalizations": [{"axis": normalization}]}
    if version is not None:
        data["__version__"] = "pyleecan_" + version
    convert_init_dict(data)
    assert normalization["__class__"] == ("NormVector" if expected else "Norm_vector")
    assert normalization["vector"] == [1, 2]


def test_convert_normalization_root_and_unrelated_dicts():
    normalization = {"__class__": "Norm_ref", "reference": 1}
    convert_init_dict(normalization)
    assert normalization == {"__class__": "NormRef", "reference": 1}
    data = {"__class__": "Data", "child": {"value": "Norm_ref"}}
    convert_init_dict(data)
    assert data == {"__class__": "Data", "child": {"value": "Norm_ref"}}
