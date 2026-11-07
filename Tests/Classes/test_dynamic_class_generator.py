"""Tests for dynamic class imports in generated code."""

import ast
import importlib
import importlib.util
import os
import shutil
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from pyleecan.Classes.Magnetics import Magnetics
from pyleecan.Classes.Simu1 import Simu1
from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.class_generator import (
    _remove_redundant_experimental_class_imports,
    _rename_experimental_normalizations,
    _replace_dynamic_class_imports,
    generate_class,
)
from pyleecan.Generator.ClassGenerator.init_method_generator import (
    generate_set_class_by_dict,
    generate_set_class_by_dict_dict,
    generate_set_class_by_dict_list,
)
from pyleecan.Generator.read_fct import read_all


@pytest.mark.parametrize(
    "expression",
    [
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics",
        'module = __import__(PACKAGE_NAME + ".Classes.Magnetics", fromlist=["Magnetics"])\n'
        '    cls = getattr(module, "Magnetics")',
        'name = "Magnetics"\n'
        '    module = __import__("pyleecan.Classes." + name, fromlist=[name])\n'
        "    cls = getattr(module, name)",
    ],
)
def test_recognized_imports_return_the_class(expression):
    source = "def method():\n    " + expression + "\n    return cls\n"
    result, changed = _replace_dynamic_class_imports(source, "pyleecan")
    assert changed
    assert "__import__" not in result
    namespace = {"_pyleecan_import_class": import_class, "PACKAGE_NAME": "pyleecan"}
    exec(result, namespace)
    assert namespace["method"]() is Magnetics


@pytest.mark.parametrize(
    "body",
    [
        'module = __import__("os.path", fromlist=["join"])\n    cls = module.join',
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n    return module",
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n    getattr = lambda *args: None",
        'module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"]) # comment\n'
        "    cls = module.Magnetics",
    ],
)
def test_unrecognized_or_unsafe_import_is_unchanged(body):
    source = "def method():\n    " + body + "\n"
    assert _replace_dynamic_class_imports(source, "pyleecan") == (source, False)


def test_redundant_dynamic_loads_reuse_experimental_header():
    source = (
        "from pyleecan.Classes_new.norm_vector import Norm_vector\n"
        "from pyleecan.Functions.Load.import_class import import_class\n"
        "class Sample:\n"
        "    def method(self, operation):\n"
        '        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n'
        "        Norm_vector = module.Norm_vector\n"
        "        result = Norm_vector\n"
        "        if operation:\n"
        "            module = operation\n"
        "            result = module.value\n"
        "        return result\n"
        "    def helper(self):\n"
        '        other = import_class("pyleecan.Classes", "Norm_vector")\n'
        "        return other\n"
    )
    transformed = _remove_redundant_experimental_class_imports(
        source, "pyleecan", {"Norm_vector": {}}
    )
    assert "__import__" not in transformed
    assert "other = Norm_vector" in transformed
    method_class = next(
        node for node in ast.parse(transformed).body if isinstance(node, ast.ClassDef)
    )
    namespace = {"Norm_vector": object()}
    exec(  # noqa: S102
        compile(
            ast.fix_missing_locations(ast.Module(body=[method_class], type_ignores=[])),
            "<test>",
            "exec",
        ),
        namespace,
    )
    instance = namespace["Sample"]()
    assert instance.method(None) is namespace["Norm_vector"]
    assert instance.method(SimpleNamespace(value=42)) == 42
    assert instance.helper() is namespace["Norm_vector"]


@pytest.mark.parametrize(
    "body",
    [
        (
            '        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n'
            "        Norm_vector = module.Norm_vector\n"
            "        return module\n"
        ),
        (
            '        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n'
            "        Norm_vector = module.Norm_vector\n"
            "        Norm_vector = None\n"
        ),
        (
            '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector")\n'
            "        return Norm_vector\n"
            "        Norm_vector = None\n"
        ),
        (
            '        Norm_vector = import_class("pyleecan.Classes", name)\n'
            "        return Norm_vector\n"
        ),
        (
            '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector")  # keep\n'
            "        return Norm_vector\n"
        ),
        '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector"); return Norm_vector\n',
        (
            '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector")\n'
            "        import_class = None\n"
        ),
        (
            "        print(Norm_vector)\n"
            '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector")\n'
        ),
        (
            "        if name:\n"
            '            Norm_vector = import_class("pyleecan.Classes", "Norm_vector")\n'
            "        return Norm_vector\n"
        ),
    ],
)
def test_redundant_dynamic_load_unsafe_cases_unchanged(body):
    source = (
        "from pyleecan.Classes_new.norm_vector import Norm_vector\n"
        "from pyleecan.Functions.Load.import_class import import_class\n"
        "class Sample:\n"
        "    def method(self, name=None):\n" + body
    )
    assert (
        _remove_redundant_experimental_class_imports(
            source, "pyleecan", {"Norm_vector": {}}
        )
        == source
    )


def test_redundant_dynamic_load_with_conditional_header_conflict_is_unchanged():
    source = (
        "from pyleecan.Classes_new.norm_vector import Norm_vector\n"
        "from pyleecan.Functions.Load.import_class import import_class\n"
        "if condition:\n"
        "    from other import Norm_vector\n"
        "class Sample:\n"
        "    def method(self):\n"
        '        Norm_vector = import_class("pyleecan.Classes", "Norm_vector")\n'
        "        return Norm_vector\n"
    )
    assert (
        _remove_redundant_experimental_class_imports(
            source, "pyleecan", {"Norm_vector": {}}
        )
        == source
    )


def test_dynamic_load_without_header_binding_is_unchanged():
    source = (
        "class Sample:\n"
        "    def method(self):\n"
        '        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n'
        "        Norm_vector = module.Norm_vector\n"
        "        return Norm_vector\n"
    )
    assert (
        _remove_redundant_experimental_class_imports(
            source, "pyleecan", {"Norm_vector": {}}
        )
        == source
    )


def test_normalization_alias_and_unshadowed_dynamic_imports():
    source = (
        "from pyleecan.Classes_new.norm_ref import Norm_ref as Reference\n"
        "class Sample:\n"
        "    def method(self):\n"
        '        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n'
        "        Norm_vector = module.Norm_vector\n"
        "        return Reference, Norm_vector\n"
    )
    transformed = _rename_experimental_normalizations(source, "pyleecan")
    assert (
        "from pyleecan.Classes_new.norm_ref import NormRef as Reference" in transformed
    )
    assert "'pyleecan.Classes_new.norm_vector'" in transformed
    assert "NormVector = module.NormVector" in transformed
    assert "return Reference, NormVector" in transformed


@pytest.mark.parametrize(
    "source",
    [
        "def method(Norm_vector):\n    return Norm_vector\n",
        "def method():\n    global Norm_vector\n",
        "from other import Norm_vector\ndef method():\n    return Norm_vector\n",
        "def method():\n    Norm_vector = NormVector\n",
        'def method():\n    return __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])\n',
    ],
)
def test_normalization_rename_rejects_conflicting_bindings(source):
    with pytest.raises(ValueError, match="normalization"):
        _rename_experimental_normalizations(source, "pyleecan")


@pytest.mark.parametrize("class_name", ["Data1D", "DataLinspace"])
@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_get_values_reuses_norm_vector(
    tmp_path, monkeypatch, class_name, import_style
):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict[class_name] = deepcopy(gen_dict[class_name])
    gen_dict[class_name]["methods"] = ["get_values", "get_axis_periodic"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "SciDataTool" / class_name
    methods.mkdir(parents=True)
    for method in gen_dict[class_name]["methods"]:
        shutil.copy2(
            Path(MAIN_DIR) / "Methods" / "SciDataTool" / class_name / (method + ".py"),
            methods,
        )
    path = generate_class(
        gen_dict,
        class_name,
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "Classes.Norm_vector" not in source
    expected = (
        "from .norm_vector import NormVector"
        if import_style == "relative"
        else "from pyleecan.Classes_new.norm_vector import NormVector"
    )
    assert expected in source
    tree = ast.parse(source)
    cls = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    method = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "get_values"
    )
    namespace = {
        "np": np,
        "NormVector": type(
            "NormVector",
            (),
            {
                "normalize": lambda self, values: self.vector.copy(),
            },
        ),
        "rebuild_symmetries_axis": lambda values, symmetries: values * 2,
        "import_module": lambda name: SimpleNamespace(
            identity=lambda values, is_real: values
        ),
    }
    exec(  # noqa: S102
        compile(
            ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
            "<test>",
            "exec",
        ),
        namespace,
    )
    norm = namespace["NormVector"]()
    norm.unit = "SI"
    norm.vector = np.array([3, 4])
    axis = SimpleNamespace(
        unit="SI",
        name="time",
        normalizations={"test": norm},
        symmetries={},
        initial=0,
        final=1,
        number=2,
        include_endpoint=True,
        values=np.array([0, 1]),
    )
    result = namespace["get_values"](axis, normalization="test", operation="identity")
    np.testing.assert_array_equal(result, [6, 8])
    np.testing.assert_array_equal(norm.vector, [3, 4])


@pytest.mark.parametrize("class_name", ["Data1D", "DataLinspace"])
def test_generated_get_values_without_header_uses_new_normalization(
    tmp_path, monkeypatch, class_name
):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict[class_name] = deepcopy(gen_dict[class_name])
    gen_dict[class_name]["methods"] = ["get_values"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "SciDataTool" / class_name
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "SciDataTool" / class_name / "get_values.py",
        methods,
    )
    path = generate_class(
        gen_dict, class_name, str(output), is_new=True, class_import_graph={}
    )
    source = Path(path).read_text(encoding="utf-8")
    assert '"pyleecan.Classes_new.norm_vector"' in source
    assert 'fromlist=["NormVector"]' in source
    assert "NormVector = module.NormVector" in source
    assert "Classes.Norm_vector" not in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_renamed_normalizations_and_legacy_serialization(
    tmp_path, monkeypatch, import_style
):
    import pyleecan.Classes_new
    from pyleecan.Classes_new._pyleecan_class import PyleecanClass
    from pyleecan.Functions.Load.retrocompatibility import (
        construct_experimental_class,
        import_experimental_class,
    )

    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    names = ["Normalization", *NORMALIZATION_CLASS_NAMES]
    data_definition = deepcopy(gen_dict["Data"])
    data_definition["methods"] = ["_set_normalizations"]
    data_gen_dict = {**gen_dict, "Data": data_definition}
    data_methods = tmp_path / "Methods" / "SciDataTool" / "Data"
    data_methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "SciDataTool" / "Data" / "_set_normalizations.py",
        data_methods,
    )
    gen_dict = {name: deepcopy(gen_dict[name]) for name in names}
    output = tmp_path / "Classes_new"
    output.mkdir()
    data_path = generate_class(
        data_gen_dict,
        "Data",
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    data_source = Path(data_path).read_text(encoding="utf-8")
    assert "Functions.Load.retrocompatibility import" in data_source
    assert "_pyleecan_class import construct_experimental_class" not in data_source
    expected_check = (
        "from ._check import check_var"
        if import_style == "relative"
        else "from pyleecan.Classes_new._check import check_var"
    )
    assert expected_check in data_source
    for name in names:
        original = Path(MAIN_DIR) / "Methods" / "SciDataTool" / name
        if original.is_dir():
            shutil.copytree(original, tmp_path / "Methods" / "SciDataTool" / name)
        generate_class(
            gen_dict,
            name,
            str(output),
            is_new=True,
            import_style=import_style,
            class_import_graph={},
        )
    monkeypatch.setattr(
        pyleecan.Classes_new, "__path__", [str(output), *pyleecan.Classes_new.__path__]
    )
    module_names = [
        "normalization",
        *(name.lower() for name in NORMALIZATION_CLASS_NAMES),
    ]
    for name in module_names:
        monkeypatch.delitem(sys.modules, f"pyleecan.Classes_new.{name}", raising=False)
    importlib.invalidate_caches()
    try:
        for old_name, new_name in NORMALIZATION_CLASS_NAMES.items():
            module = importlib.import_module("pyleecan.Classes_new." + old_name.lower())
            cls = getattr(module, new_name)
            assert cls.__name__ == new_name
            assert not hasattr(module, old_name)
            assert import_experimental_class("pyleecan.Classes", old_name) is cls
            assert import_experimental_class("pyleecan.Classes", new_name) is cls
            assert (
                cls.from_dict({"__class__": old_name}).as_dict()["__class__"]
                == new_name
            )
        norm_vector = import_experimental_class("pyleecan.Classes", "NormVector")
        from pyleecan.Classes.Norm_vector import Norm_vector as LegacyNormVector

        assert import_class("pyleecan.Classes", "Norm_vector") is LegacyNormVector
        assert import_experimental_class("pyleecan.Classes", "Norm_vector") is norm_vector
        legacy = construct_experimental_class(
            LegacyNormVector, {"__class__": "Norm_vector", "vector": [5, 6]}
        )
        assert isinstance(legacy, LegacyNormVector)
        for serialized_name in ("Norm_vector", "NormVector"):
            loaded = norm_vector.from_dict(
                {"__class__": serialized_name, "vector": [1.0, 2.0]}
            )
            np.testing.assert_array_equal(loaded.vector, [1.0, 2.0])

        from dataclasses import dataclass, field

        normalization = importlib.import_module("pyleecan.Classes_new.normalization")

        @dataclass
        class Holder(PyleecanClass):
            normalizations: dict[str, normalization.Normalization] = field(
                default_factory=dict
            )

            def __post_init__(self):
                super().__post_init__()

        from pyleecan.Functions.Load.retrocompatibility import (
            load_experimental_normalization_values,
        )

        nested = load_experimental_normalization_values(
            {"untouched": 1, "values": [[{"__class__": "Norm_vector", "vector": [7]}]]}
        )
        assert nested["untouched"] == 1
        assert isinstance(nested["values"][0][0], norm_vector)

        for serialized_name in ("Norm_vector", "NormVector"):
            holder = Holder.from_dict(
                {
                    "normalizations": {
                        "axis": {"__class__": serialized_name, "vector": [1, 2]}
                    }
                }
            )
            assert type(holder.normalizations["axis"]) is norm_vector
            assert (
                holder.as_dict()["normalizations"]["axis"]["__class__"] == "NormVector"
            )

        from pyleecan.Classes_new._check import check_var
        tree = ast.parse(Path(data_path).read_text(encoding="utf-8"))
        data_class = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        setter = next(
            node
            for node in data_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "_set_normalizations"
        )
        namespace = {
            "np": np,
            "check_var": check_var,
            "_import_experimental_class": import_experimental_class,
            "_construct_experimental_class": construct_experimental_class,
        }
        exec(  # noqa: S102
            compile(
                ast.fix_missing_locations(ast.Module(body=[setter], type_ignores=[])),
                "<test>",
                "exec",
            ),
            namespace,
        )
        axis = SimpleNamespace()
        for serialized_name in ("Norm_vector", "NormVector"):
            namespace["_set_normalizations"](
                axis,
                {
                    "v": {"__class__": serialized_name, "vector": [1, 2]},
                    "r": 3.0,
                    "list": [3, 4],
                },
            )
            assert type(axis._normalizations["v"]) is norm_vector
            assert type(axis._normalizations["r"]).__name__ == "NormRef"
            np.testing.assert_array_equal(axis._normalizations["list"].vector, [3, 4])
            assert isinstance(axis._normalizations["list"].vector, np.ndarray)
    finally:
        for name in module_names:
            sys.modules.pop("pyleecan.Classes_new." + name, None)


@pytest.mark.parametrize(
    "generator",
    [
        generate_set_class_by_dict,
        generate_set_class_by_dict_list,
        generate_set_class_by_dict_dict,
    ],
)
def test_constructor_class_imports_use_shared_helper(generator):
    source = generator("item", "Magnetics", ["MagFEMM"])
    assert 'import_class("pyleecan.Classes", class_name, "item")' in source
    assert "__import__" not in source


@pytest.mark.parametrize("is_new", [False, True])
def test_generated_method_uses_import_class(tmp_path, monkeypatch, is_new):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Magnetics"] = deepcopy(gen_dict["Magnetics"])
    gen_dict["Magnetics"]["methods"] = ["comp_axes"]
    output = tmp_path / "Classes"
    output.mkdir()
    methods = tmp_path / "Methods" / "Simulation" / "Magnetics"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "def comp_axes(self):\n"
        '    module = __import__("pyleecan.Classes.Magnetics", fromlist=["Magnetics"])\n'
        "    cls = module.Magnetics\n"
        "    return cls\n",
        encoding="utf-8",
    )
    generate_class(
        gen_dict, "Magnetics", str(output), is_new=is_new, class_import_graph={}
    )
    path = output / ("magnetics.py" if is_new else "Magnetics.py")
    module = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "Magnetics"
    )
    method = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "comp_axes"
    )
    body = ast.unparse(method)
    assert "_pyleecan_import_class('pyleecan.Classes', 'Magnetics')" in body
    assert "__import__" not in body
    namespace = {"_pyleecan_import_class": import_class}
    exec(body, namespace)
    assert namespace["comp_axes"](None) is Magnetics
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module.endswith("Functions.Load.import_class")
        and any(alias.asname == "_pyleecan_import_class" for alias in node.names)
        for node in module.body
        if isinstance(node, ast.ImportFrom) and node.module
    )


def test_generated_legacy_constructor_loads_subclass(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Output"] = deepcopy(gen_dict["Output"])
    gen_dict["Output"]["methods"] = []
    generate_class(gen_dict, "Output", str(tmp_path), class_import_graph={})
    path = tmp_path / "Output.py"
    spec = importlib.util.spec_from_file_location(
        "pyleecan.Classes.test_generated_output", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = module.Output(simu=Simu1().as_dict())
    assert isinstance(output.simu, Simu1)
