import gzip
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

from pyleecan.Classes_new._error import InitUnKnowClassError, LoadMissingFileError
from pyleecan.Classes_new.data_linspace import DataLinspace
from pyleecan.Classes_new.data_time import DataTime
from pyleecan.Classes_new.input_current import InputCurrent
from pyleecan.Classes_new.lam_slot_wind import LamSlotWind
from pyleecan.Classes_new.machine_ipmsm import MachineIPMSM
from pyleecan.Classes_new.material import Material
from pyleecan.Classes_new.norm_ref import NormRef
from pyleecan.Classes_new.op_dq import OPdq
from pyleecan.Classes_new.op_matrix import OPMatrix
from pyleecan.Classes_new.var_load_current import VarLoadCurrent
from pyleecan.Classes_new.var_param_sweep import VarParamSweep
from pyleecan.Functions_new.load import load, load_dict, load_list
from pyleecan.Functions_new.Load.retrocompatibility import convert_init_dict
from pyleecan.Generator.ClassGenerator.New.class_generator import _field_type
from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
    _adapt_json_load,
    _adapt_json_retrocompatibility,
    _adapt_retrocompatibility,
    generate_functions,
)

ROOT = Path(__file__).resolve().parents[2]


def write_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file)


@pytest.mark.parametrize("compressed", [False, True])
def test_load_material_and_legacy_null(tmp_path, compressed):
    data = {
        "__class__": "Material",
        "struct": {"__class__": "MatStructural", "Ey": None},
    }
    path = tmp_path / ("material.json.gz" if compressed else "material.json")
    if compressed:
        with gzip.open(path, "wt", encoding="utf-8") as file:
            json.dump(data, file)
    else:
        write_json(path, data)
    material = load(str(path))
    assert isinstance(material, Material)
    assert material.struct.Ey is None
    assert material.struct.parent is material


def test_nested_subclasses_and_arrays(tmp_path):
    path = tmp_path / "objects.json"
    write_json(
        path,
        [
            {"__class__": "MachineIPMSM", "stator": {"__class__": "LamSlotWind"}},
            {
                "__class__": "DataTime",
                "axes": [{"__class__": "DataLinspace"}],
                "values": [1, 2],
            },
        ],
    )
    machine, data = load_list(str(path))
    assert isinstance(machine, MachineIPMSM)
    assert isinstance(machine.stator, LamSlotWind)
    assert machine.stator.parent is machine
    assert isinstance(data, DataTime)
    assert isinstance(data.axes[0], DataLinspace)
    assert data.axes[0].parent is data
    assert isinstance(data.values, np.ndarray)


def test_nested_collections_and_old_versions(tmp_path):
    path = tmp_path / "objects.json"
    write_json(
        path, {"objects": [[{"__class__": "Norm_ref"}, {"__class__": "VarParam"}]]}
    )
    result = load_dict(str(path))
    assert isinstance(result["objects"][0][0], NormRef)
    assert isinstance(result["objects"][0][1], VarParamSweep)


def test_split_references_relative_to_each_file(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_json(
        tmp_path / "machine.json",
        {"__class__": "MachineIPMSM", "stator": "nested/stator.json"},
    )
    write_json(
        nested / "stator.json",
        {"__class__": "LamSlotWind", "mat_type": "material.json.gz"},
    )
    with gzip.open(nested / "material.json.gz", "wt", encoding="utf-8") as file:
        json.dump({"__class__": "Material", "name": "nested"}, file)
    machine = load(str(tmp_path / "machine.json"))
    assert isinstance(machine.stator, LamSlotWind)
    assert isinstance(machine.stator.mat_type, Material)
    assert machine.stator.mat_type.name == "nested"
    assert machine.stator.mat_type.parent is machine.stator
    (nested / "material.json.gz").unlink()
    with pytest.raises(LoadMissingFileError):
        load(str(tmp_path / "machine.json"))


def test_unknown_and_incompatible_classes(tmp_path):
    path = tmp_path / "machine.json"
    write_json(
        path, {"__class__": "MachineIPMSM", "stator": {"__class__": "NoSuchClass"}}
    )
    with pytest.raises(InitUnKnowClassError):
        load(str(path))
    write_json(path, {"__class__": "MachineIPMSM", "stator": {"__class__": "Material"}})
    with pytest.raises(TypeError, match="incompatible"):
        load(str(path))


def test_conversion_continues_after_migration():
    data = {
        "__class__": "SlotM10",
        "Hmag": 2,
        "child": [[{"__class__": "Norm_ref"}]],
    }
    convert_init_dict(data)
    assert data["H1"] == 2
    assert data["child"][0][0]["__class__"] == "NormRef"
    empty_hole = {"__class__": "HoleUD", "surf_list": []}
    convert_init_dict(empty_hole)
    assert empty_hole["surf_list"] == []


def test_legacy_operating_points(tmp_path):
    path = tmp_path / "input.json"
    write_json(
        path,
        {
            "__class__": "InputCurrent",
            "N0": 1000,
            "Id_ref": 1,
            "Iq_ref": 2,
            "Tem_av_ref": 3,
        },
    )
    result = load(str(path))
    assert isinstance(result, InputCurrent)
    assert isinstance(result.OP, OPdq)
    assert result.OP.Id_ref == 1
    assert result.OP.parent is result


def test_legacy_operating_point_matrix(tmp_path):
    path = tmp_path / "load.json"
    write_json(
        path,
        {
            "__class__": "VarLoadCurrent",
            "type_OP_matrix": 1,
            "OP_matrix": [[1000, 1, 2]],
        },
    )
    result = load(str(path))
    assert isinstance(result, VarLoadCurrent)
    assert isinstance(result.OP_matrix, OPMatrix)
    assert result.OP_matrix.parent is result
    np.testing.assert_array_equal(result.OP_matrix.Id_ref, [1])


def test_field_type_name_collision_is_aliased():
    annotation, imports = _field_type(
        "OP", "None", {"OP": {}}, "pyleecan", "Input", "OP"
    )
    assert annotation == "_field_type_OP | None"
    assert "from pyleecan.Classes.OP import OP as _field_type_OP" in imports


@pytest.mark.parametrize(
    "path",
    [
        ROOT / "src" / "pyleecan" / "Data" / "Machine" / "Toyota_Prius.json",
        ROOT
        / "Tests"
        / "Data"
        / "Retrocompatibility"
        / "Winding"
        / "Toyota_Prius.json",
    ],
)
def test_real_machine_files(path):
    machine = load(str(path))
    assert isinstance(machine, MachineIPMSM)
    assert isinstance(machine.stator, LamSlotWind)
    assert machine.stator.parent is machine


def test_loader_generator_transformations_compile():
    functions = ROOT / "src" / "pyleecan" / "Functions"
    load_path = functions / "load.py"
    retro_path = functions / "Load" / "retrocompatibility.py"
    load_source = _adapt_json_load(load_path.read_text(encoding="utf-8"), load_path)
    retro_source = _adapt_retrocompatibility(
        retro_path.read_text(encoding="utf-8"), retro_path
    )
    retro_source = _adapt_json_retrocompatibility(retro_source, retro_path)
    compile(load_source, str(load_path), "exec")
    compile(retro_source, str(retro_path), "exec")
    assert "class_obj.from_dict(obj, base_path=folder_path)" in load_source
    assert 'obj_dict["__class__"] = "VarParamSweep"' in retro_source


def test_generated_loader_modules_match(tmp_path, monkeypatch):
    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    source = tmp_path / "Functions"
    (source / "Load").mkdir(parents=True)
    original = ROOT / "src" / "pyleecan" / "Functions"
    generated = ROOT / "src" / "pyleecan" / "Functions_new"
    for path in (Path("load.py"), Path("Load") / "retrocompatibility.py"):
        shutil.copyfile(original / path, source / path)
    output = tmp_path / "Functions_new"
    generate_functions(source, output, ROOT / "src" / "pyleecan" / "Classes_new")
    for path in (Path("load.py"), Path("Load") / "retrocompatibility.py"):
        assert (output / path).read_text(encoding="utf-8") == (
            generated / path
        ).read_text(encoding="utf-8")
