"""Step 13: custom property setters (simulation package) on both backends."""

from typing import Any

import pytest

from backend_classes._import import import_class
from pyleecan.classes_common.functions import (
    SourceFunction,
    legacy_function_source,
    resolve_wildcard_path,
)
from pyleecan.classes_common.legacy_values import holds_pyleecan_objects


def test_legacy_function_source():
    assert legacy_function_source("simu.machine.rotor.slot.W0", "getter") == (
        "lambda simu: getattr(eval('simu.machine.rotor.slot'), 'W0')"
    )
    assert legacy_function_source("simu.input", "setter") == (
        "lambda simu, val: setattr(eval('simu'), 'input', val)"
    )
    assert legacy_function_source("lambda x: x", "setter") == "lambda x: x"
    assert legacy_function_source(None, "getter") is None


def test_resolve_wildcard_path():
    from pyleecan.definitions import DATA_DIR

    assert resolve_wildcard_path("<DATA_DIR>/a/b.py") == (
        DATA_DIR.replace("\\", "/").rstrip("/") + "/a/b.py"
    )
    assert resolve_wildcard_path("C:/x/b.py") == "C:/x/b.py"
    assert resolve_wildcard_path("<UNKNOWN_DIR>/b.py") == "<UNKNOWN_DIR>/b.py"


def test_holds_pyleecan_objects():
    Output = import_class("Output")
    assert holds_pyleecan_objects(Output)
    assert holds_pyleecan_objects(list[Output] | None)
    assert holds_pyleecan_objects(dict[str, Output])
    assert not holds_pyleecan_objects(list[Any] | None)
    assert not holds_pyleecan_objects(float)
    assert holds_pyleecan_objects("Output")  # Not resolved: kept


def test_param_explorer_setter_and_getter_from_simulation_path():
    ParamExplorerSet = import_class("ParamExplorerSet")
    InputCurrent = import_class("InputCurrent")
    explorer = ParamExplorerSet(setter="simu.input", getter="simu.input", value=[])
    assert isinstance(explorer.setter, SourceFunction)

    class Simu:
        input = None

    simu = Simu()
    explorer.setter(simu, 3)
    assert simu.input == 3 and explorer.getter(simu) == 3
    # Saved by its lambda source, reloaded the same
    data = explorer.as_dict()
    assert "lambda simu, val" in data["setter"]
    assert ParamExplorerSet(init_dict=data).as_dict() == data
    # A list of plain values keeps the parent of its objects
    current = InputCurrent()
    ParamExplorerSet(setter="simu.input", value=[current])
    assert current.parent is None


def test_data_keeper_keeper_lambda_with_numpy_names():
    DataKeeper = import_class("DataKeeper")
    keeper = DataKeeper(keeper="lambda output: sqrt(4) + pi * 0 + np.abs(-1)")
    assert keeper.keeper(None) == 3


def test_var_load_op_matrix_from_list():
    VarLoadCurrent = import_class("VarLoadCurrent")
    OPMatrix = import_class("OPMatrix")
    varload = VarLoadCurrent()
    varload.OP_matrix = [[1, 2, 3, 4], [5, 6, 7, 8]]
    assert isinstance(varload.OP_matrix, OPMatrix)
    assert varload.OP_matrix.parent is varload


def test_object_list_accepts_none_items():
    XOutput = import_class("XOutput")
    xoutput = XOutput()
    xoutput.output_list = [None, None]
    assert xoutput.output_list == [None, None]


def test_femm_handler_dump_is_loaded():
    from pyleecan.classes_common.femm_handler import _FEMMHandler

    assert import_class("_FEMMHandler") is _FEMMHandler
    OutMagFEMM = import_class("OutMagFEMM")
    dump = {"__class__": "_FEMMHandler", "HandleToFEMM": None}
    out = OutMagFEMM.from_dict({"__class__": "OutMagFEMM", "handler_list": [dump]})
    assert isinstance(out.handler_list[0], _FEMMHandler)  # Loaded (both backends)


def test_invalid_function_rejected():
    ParamExplorerSet = import_class("ParamExplorerSet")
    with pytest.raises(Exception):
        ParamExplorerSet(setter=3)
