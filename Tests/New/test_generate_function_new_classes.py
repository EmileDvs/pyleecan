import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pyleecan.Generator.ClassGenerator.New import generate_function_new_classes
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _apply_import_style,
    _redirect_experimental_function_imports,
)
from pyleecan.Generator.ClassGenerator.New.function_module_names import (
    function_module_mapping,
    function_module_name,
    redirect_function_module_imports,
    redirect_rule_module_name,
)
from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
    _adapt_retrocompatibility,
    _format_function_source,
    _function_import_style,
    _redirect_function_errors,
    _redirect_shared_error_imports,
    _rewrite_source,
    generate_functions,
)


def test_function_module_names_and_imports(tmp_path):
    source = tmp_path / "Functions"
    (source / "FEMM").mkdir(parents=True)
    (source / "FEMM" / "comp_FEMM_dict.py").touch()
    (source / "FEMM" / "__init__.py").touch()
    mapping = function_module_mapping(source)
    assert mapping == {"FEMM.comp_FEMM_dict": "FEMM.comp_femm_dict"}
    assert function_module_name("plot_4D") == "plot_4d"
    assert function_module_name("curve_B(H)") == "curve_bh"
    assert function_module_name("__init__") == "__init__"
    text = (
        "from .comp_FEMM_dict import comp_FEMM_dict\n"
        "from pyleecan.Functions_new.FEMM import comp_FEMM_dict\n"
        "import pyleecan.Functions_new.FEMM.comp_FEMM_dict as helper\n"
        "value = import_module('pyleecan.Functions_new.FEMM.comp_FEMM_dict')\n"
        "module = pyleecan.Functions_new.FEMM.comp_FEMM_dict\n"
        "note = 'comp_FEMM_dict'\n"
    )
    result = redirect_function_module_imports(
        text, "pyleecan.Functions_new.FEMM", mapping
    )
    assert "from .comp_femm_dict import comp_FEMM_dict" in result
    assert "import comp_femm_dict as comp_FEMM_dict" in result
    assert "import pyleecan.Functions_new.FEMM.comp_femm_dict as helper" in result
    assert "import_module('pyleecan.Functions_new.FEMM.comp_femm_dict')" in result
    assert "module = pyleecan.Functions_new.FEMM.comp_femm_dict" in result
    assert "note = 'comp_FEMM_dict'" in result


def test_function_module_mapping_rejects_collisions(tmp_path):
    (tmp_path / "Foo.py").touch()
    (tmp_path / "foo.py").touch()
    if len(list(tmp_path.iterdir())) < 2:
        pytest.skip("Case-insensitive filesystem")
    with pytest.raises(ValueError, match="collision"):
        function_module_mapping(tmp_path)


def test_rule_module_name_conversion_keeps_legacy_values():
    source = (
        'name = f"pyleecan.Functions_new.Converter.MotorCAD.{self.fct_name}"\n'
    )
    result = redirect_rule_module_name(source)
    from types import SimpleNamespace

    for name in ("curve_B(H)", "slotW11_H1", "skew"):
        namespace = {"self": SimpleNamespace(fct_name=name)}
        exec(result, namespace)  # noqa: S102
        assert namespace["name"].endswith("." + function_module_name(name))


def test_generate_functions_renames_modules_and_references(tmp_path):
    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    (source / "FEMM").mkdir(parents=True)
    classes.mkdir()
    (source / "FEMM" / "comp_FEMM_dict.py").write_text(
        "def comp_FEMM_dict():\n    return 3\n", encoding="utf-8"
    )
    (source / "FEMM" / "draw.py").write_text(
        "from .comp_FEMM_dict import comp_FEMM_dict\n", encoding="utf-8"
    )
    generate_functions(source, output, classes)
    assert (output / "FEMM" / "comp_femm_dict.py").exists()
    assert not (output / "FEMM" / "comp_FEMM_dict.py").exists() or (
        output / "FEMM" / "comp_FEMM_dict.py"
    ).samefile(output / "FEMM" / "comp_femm_dict.py")
    assert "from .comp_femm_dict import comp_FEMM_dict" in (
        output / "FEMM" / "draw.py"
    ).read_text(encoding="utf-8")


def test_rewrite_imports_and_report_unresolved(tmp_path):
    class_dir = tmp_path / "Classes_new"
    class_dir.mkdir()
    for module in ("arc_1", "norm_ref", "segment"):
        (class_dir / (module + ".py")).touch()
    source = (
        "# from ...Classes.Arc1 import Arc1\n"
        "message = 'pyleecan.Classes.Arc1'\n"
        "from ...Classes.Arc1 import Arc1 as Arc\n"
        "from pyleecan.Classes.Norm_ref import Norm_ref\n"
        "from ...Functions.Electrical.helper import helper\n"
        "from pyleecan.Functions.Winding.gen_phase_list import gen_name\n"
        "from ..Load.import_class import import_class\n"
        "from ...Classes.import_all import *\n"
        "def make():\n"
        "    Segment = import_class('pyleecan.Classes', 'Segment')\n"
        "    return Segment\n"
    )
    result, issues = _rewrite_source(
        source, Path("sample.py"), Path("Plot") / "sample.py", class_dir
    )
    assert "# from ...Classes.Arc1 import Arc1" in result
    assert "message = 'pyleecan.Classes.Arc1'" in result
    assert "from pyleecan.Classes_new.arc_1 import Arc1 as Arc" in result
    assert "from pyleecan.Classes_new.norm_ref import NormRef as Norm_ref" in result
    assert "from ...Functions_new.Electrical.helper import helper" in result
    assert (
        "from pyleecan.Functions_new.Winding.gen_phase_list import gen_name" in result
    )
    assert "from pyleecan.Classes_new.segment import Segment" in result
    assert "from ..Load.import_class import import_class" not in result
    assert issues == [(8, "legacy import: pyleecan.Classes.import_all")]
    ast.parse(result)


def test_rewrite_vendored_class_packages(tmp_path):
    smoot = tmp_path / "_smoot"
    swat = tmp_path / "_swat_em"
    smoot.mkdir()
    swat.mkdir()
    (smoot / "__init__.py").touch()
    (swat / "datamodel.py").touch()
    source = (
        "from pyleecan.Classes._smoot import MOO as Optimizer\n"
        "from ...Classes._swat_em.datamodel import datamodel\n"
        "from ...Classes._other import Something\n"
    )
    result, issues = _rewrite_source(
        source, Path("sample.py"), Path("_smoot") / "sample.py", tmp_path
    )
    assert "from pyleecan.Classes_new._smoot import MOO as Optimizer" in result
    assert "from pyleecan.Classes_new._swat_em.datamodel import datamodel" in result
    assert issues == [(3, "legacy import: pyleecan.Classes._other")]


def test_copy_tree_keeps_resources_and_reports_deferred_loader(tmp_path):
    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    (source / "Electrical").mkdir(parents=True)
    classes.mkdir()
    (classes / "data_time.py").touch()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "Electrical" / "sample.py").write_text(
        "from ...Classes.DataTime import DataTime\n", encoding="utf-8"
    )
    (source / "copy.py").write_text(
        "obj = import_class('pyleecan.Classes', 'DataTime')\n", encoding="utf-8"
    )
    (source / "Electrical" / "fixture.lua").write_bytes(b"fixture\x00")
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "cache.pyc").write_bytes(b"cache")
    output.mkdir()
    (output / "existing.py").write_text("keep", encoding="utf-8")
    issues = generate_functions(source, output, classes)
    assert issues == [(Path("copy.py"), 1, "dynamic class loader requires review")]
    assert (output / "Electrical" / "sample.py").read_text(encoding="utf-8") == (
        "from ...Classes_new.data_time import DataTime\n"
    )
    assert (output / "Electrical" / "fixture.lua").read_bytes() == b"fixture\x00"
    assert not (output / "__pycache__").exists()
    assert (output / "existing.py").read_text() == "keep"
    assert (
        (source / "Electrical" / "sample.py")
        .read_text(encoding="utf-8")
        .startswith("from ...Classes.")
    )
    with pytest.raises(ValueError, match="separate"):
        generate_functions(source, source / "output", classes)


def test_generate_functions_uses_default_package_paths(tmp_path, monkeypatch):
    source = tmp_path / "Functions"
    classes = tmp_path / "Classes_new"
    source.mkdir()
    classes.mkdir()
    (source / "sample.py").write_text(
        "from pyleecan.Functions.load import load\n", encoding="utf-8"
    )
    monkeypatch.setattr(generate_function_new_classes, "MAIN_DIR", str(tmp_path))

    assert generate_functions() == []
    assert (tmp_path / "Functions_new" / "sample.py").read_text(
        encoding="utf-8"
    ) == "from .load import load\n"


@pytest.mark.parametrize(
    ("style", "expected"),
    [
        ("relative", "from ...Classes_new._error import DimError as Error"),
        ("absolute", "from pyleecan.Classes_new._error import DimError as Error"),
    ],
)
def test_function_import_styles_respect_package_depth(style, expected):
    source = (
        "from pyleecan.Classes_new._error import DimError as Error\n"
        "from ..Load.load_json import load_json\n"
        "def local():\n"
        "    from pyleecan.definitions import MAIN_DIR\n"
    )
    result = _function_import_style(source, "pyleecan.Functions_new.Structural", style)
    assert expected in result
    expected_load = (
        "from ..Load.load_json import load_json"
        if style == "relative"
        else "from pyleecan.Functions_new.Load.load_json import load_json"
    )
    assert expected_load in result
    assert (
        "    from ...definitions import MAIN_DIR"
        if style == "relative"
        else "    from pyleecan.definitions import MAIN_DIR"
    ) in result


@pytest.mark.parametrize(
    ("style", "expected"),
    [
        ("relative", "from ...Classes_new.data_time import DataTime"),
        ("absolute", "from pyleecan.Classes_new.data_time import DataTime"),
    ],
)
def test_generate_functions_emits_requested_import_style(tmp_path, style, expected):
    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    (source / "Electrical").mkdir(parents=True)
    classes.mkdir()
    (classes / "data_time.py").touch()
    (source / "Electrical" / "sample.py").write_text(
        "from ...Classes.DataTime import DataTime\n"
        "from numpy import array\n"
        "def make():\n    return array([1])\n",
        encoding="utf-8",
    )
    assert generate_functions(source, output, classes, import_style=style) == []
    result = (output / "Electrical" / "sample.py").read_text(encoding="utf-8")
    assert expected in result
    assert "import numpy as np" in result
    assert "return np.array([1])" in result


def test_error_imports_follow_module_docstring_and_future_import(tmp_path):
    source = (
        '# -*- coding: utf-8 -*-\n"""Module documentation."""\n'
        "from __future__ import annotations\n\n"
        "def fail():\n    raise InputError()\n\n"
        "class InputError(Exception):\n    pass\n"
    )
    (tmp_path / "_error.py").write_text(
        "class GMSHInputError(Exception): pass\n", encoding="utf-8"
    )
    result = _redirect_function_errors(source, Path("GMSH"), Path("GMSH") / "__init__.py", tmp_path)
    assert result.index("from __future__") < result.index("import GMSHInputError")
    assert result.index("import GMSHInputError") < result.index("def fail")
    assert ast.get_docstring(ast.parse(result)) == "Module documentation."
    compile(result, "generated.py", "exec")


def test_invalid_import_style_rejected(tmp_path):
    with pytest.raises(ValueError, match="import_style"):
        generate_functions(tmp_path, tmp_path, tmp_path, import_style="invalid")


def test_function_format_normalizes_numpy_and_preserves_shadowing(tmp_path):
    source = (
        "from numpy import array as make_array\n"
        "from numpy.fft import fft\n"
        "def compute(values):\n"
        "    return fft(make_array(values))\n"
    )
    transformed = _format_function_source(source, tmp_path / "sample.py")
    assert "import numpy as np" in transformed
    assert "np.fft.fft(np.array(values))" in transformed
    namespaces = [{}, {}]
    for code, namespace in zip((source, transformed), namespaces):
        exec(compile(code, "<test>", "exec"), namespace)  # noqa: S102
    import numpy as np

    np.testing.assert_array_equal(
        namespaces[0]["compute"]([1, 2]), namespaces[1]["compute"]([1, 2])
    )
    shadowed = "from numpy import array\ndef compute(np):\n    return array(np)\n"
    result = _format_function_source(shadowed, tmp_path / "shadowed.py")
    assert "from numpy import array" in result
    assert "return array(np)" in result
    dynamic = "from numpy import pi\ndef compute(value):\n    return eval(value)\n"
    result = _format_function_source(dynamic, tmp_path / "dynamic.py")
    namespace = {}
    exec(compile(result, "<test>", "exec"), namespace)  # noqa: S102
    assert namespace["compute"]("pi / 2") == np.pi / 2
    assert "from numpy import pi" in result
    comprehension = (
        "from numpy import array\n"
        "def compute(values):\n"
        "    return [array for array in values]\n"
    )
    result = _format_function_source(comprehension, tmp_path / "comprehension.py")
    namespace = {}
    exec(compile(result, "<test>", "exec"), namespace)  # noqa: S102
    assert namespace["compute"]([1, 2]) == [1, 2]


def test_function_format_replaces_unshadowed_empty_containers(tmp_path):
    source = (
        "def make():\n"
        "    text = 'list() dict() tuple()'\n"
        "    return list(), dict(), tuple(), list((1,)), dict(a=1), tuple([2])\n"
    )
    result = _format_function_source(source, tmp_path / "containers.py")
    assert "'list() dict() tuple()'" in result or '"list() dict() tuple()"' in result
    assert "return [], {}, (), list((1,)), dict(a=1), tuple([2])" in result
    shadowed = "def make(tuple):\n    return list(), dict(), tuple()\n"
    result = _format_function_source(shadowed, tmp_path / "shadowed.py")
    assert "return [], {}, tuple()" in result


def test_function_format_removes_only_utf8_header(tmp_path):
    source = "# -*- coding: utf-8 -*-\nvalue = 'é'\n"
    result = _format_function_source(source, tmp_path / "utf8.py")
    assert "coding: utf-8" not in result
    assert "é" in result
    source = "# -*- coding: latin-1 -*-\nvalue = 1\n"
    result = _format_function_source(source, tmp_path / "latin1.py")
    assert result.startswith("# -*- coding: latin-1 -*-")


def test_generated_parser_keeps_math_names_available_to_eval():
    import numpy as np

    from pyleecan.Functions_new.SciDataTool.parser import read_input_strings

    axis = read_input_strings(["angle=pi/2"], {})[0]
    assert axis.input_data == [np.pi / 2]


def test_generated_normalization_transformation(tmp_path, monkeypatch):
    from pyleecan.Classes_new import _error
    from pyleecan.definitions import MAIN_DIR

    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    (source / "Load").mkdir(parents=True)
    classes.mkdir()
    (classes / "_error.py").write_text(
        "class RetroCompatibilityError(Exception): pass\n", encoding="utf-8"
    )
    monkeypatch.setattr(_error, "RetroCompatibilityError", type(
        "RetroCompatibilityError", (Exception,), {}
    ), raising=False)
    shutil.copy2(
        Path(MAIN_DIR) / "Functions" / "Load" / "retrocompatibility.py",
        source / "Load" / "retrocompatibility.py",
    )
    generate_functions(source, output, classes)
    generated = output / "Load" / "retrocompatibility.py"
    first = generated.read_bytes()
    generate_functions(source, output, classes)
    assert generated.read_bytes() == first
    assert {
        path.relative_to(output) for path in output.rglob("*") if path.is_file()
    } == {Path("Load") / "retrocompatibility.py"}
    namespace = {"__package__": "pyleecan.Functions_new.Load"}
    exec(compile(generated.read_bytes(), str(generated), "exec"), namespace)  # noqa: S102
    for version, expected in (("1.5.1", "NormVector"), ("1.5.2", "Norm_vector")):
        nested = {"__class__": "Norm_vector", "vector": [1, 2]}
        data = {
            "__class__": "Data",
            "__version__": "pyleecan_" + version,
            "normalizations": [nested],
        }
        namespace["convert_init_dict"](data)
        assert nested == {"__class__": expected, "vector": [1, 2]}
    for name in (
        "import_experimental_class",
        "construct_experimental_class",
        "load_experimental_normalization_values",
    ):
        assert name not in namespace


def test_normalization_transformation_reports_source_drift(tmp_path):
    from pyleecan.definitions import MAIN_DIR

    source = (
        Path(MAIN_DIR) / "Functions" / "Load" / "retrocompatibility.py"
    ).read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="expected exactly one function"):
        _adapt_retrocompatibility(
            source.replace("def _search_and_update(", "def renamed("),
            tmp_path / "retrocompatibility.py",
        )
    with pytest.raises(ValueError, match="normalization name mapping already exists"):
        _adapt_retrocompatibility(
            source + "\nNORMALIZATION_CLASS_NAMES = {}\n",
            tmp_path / "retrocompatibility.py",
        )


def test_function_error_rewrite_rejects_missing_or_stale_shared_classes(tmp_path):
    source = "class InputError(Exception):\n    pass\n\ndef fail():\n    raise InputError()\n"
    path = tmp_path / "GMSH" / "__init__.py"
    relative = Path("GMSH") / "__init__.py"
    with pytest.raises(FileNotFoundError, match="generate classes first"):
        _redirect_function_errors(source, path, relative, tmp_path)
    errors = tmp_path / "_error.py"
    errors.write_text("class GMSHInputError(ValueError): pass\n", encoding="utf-8")
    with pytest.raises(ValueError, match="incompatible GMSHInputError"):
        _redirect_function_errors(source, path, relative, tmp_path)
    errors.write_text("class GMSHInputError(Exception): pass\n", encoding="utf-8")
    result = _redirect_function_errors(source, path, relative, tmp_path)
    assert "import GMSHInputError as InputError" in result
    with pytest.raises(ValueError, match="missing function exceptions"):
        _redirect_function_errors("pass\n", path, relative, tmp_path)


def test_shared_error_imports_preserve_other_imports_and_aliases():
    source = (
        "from pyleecan.Functions.GMSH import InputError, draw_GMSH\n"
        "from ..SciDataTool import AxisError as Axis, axes_dict\n"
        "text = 'pyleecan.Functions.GMSH.InputError'\n"
    )
    result = _redirect_shared_error_imports(source, "pyleecan.Functions_new.Plot")
    assert "from pyleecan.Functions.GMSH import draw_GMSH" in result
    assert "from pyleecan.Classes_new._error import GMSHInputError as InputError" in result
    assert "from ..SciDataTool import axes_dict" in result
    assert "from pyleecan.Classes_new._error import AxisError as Axis" in result
    assert "text = 'pyleecan.Functions.GMSH.InputError'" in result
    ast.parse(result)


def test_generator_removes_only_obsolete_error_modules(tmp_path):
    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    source_module = source / "Converter" / "Utils" / "ConvertionError.py"
    target_module = output / "Converter" / "Utils" / "ConvertionError.py"
    source_module.parent.mkdir(parents=True)
    target_module.parent.mkdir(parents=True)
    classes.mkdir()
    source_module.write_text("class ConvertionError(Exception): pass\n", encoding="utf-8")
    (classes / "_error.py").write_text(
        "class ConvertionError(Exception): pass\n", encoding="utf-8"
    )
    target_module.write_text(
        "from pyleecan.Classes_new._error import ConvertionError\n", encoding="utf-8"
    )
    assert generate_functions(source, output, classes) == []
    assert not target_module.exists()
    target_module.write_text("custom_value = 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="refusing to remove modified module"):
        generate_functions(source, output, classes)
    assert target_module.read_text(encoding="utf-8") == "custom_value = 1\n"


def test_shared_function_errors_end_to_end(tmp_path, monkeypatch):
    from pyleecan.definitions import MAIN_DIR
    from pyleecan.Generator.ClassGenerator.New import class_generator
    from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
        FUNCTION_ERRORS,
    )

    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    package_root = tmp_path / "pyleecan"
    classes = package_root / "Classes_new"
    classes.mkdir(parents=True)
    (classes / "__init__.py").write_text("", encoding="utf-8")
    legacy_classes = str(Path(MAIN_DIR) / "Classes_new")
    definitions = {}
    for module, errors in FUNCTION_ERRORS.items():
        module_name = "pyleecan.Functions." + module
        for name in errors:
            for definition in class_generator._get_error_class_definitions(
                legacy_classes, module_name, name
            ):
                definitions[definition.error_origin] = definition
    assert len(definitions) == 20
    for module, name in (
        ("pyleecan.Methods.Simulation.Input", "InputError"),
        ("pyleecan.Methods.Import", "ImportError"),
    ):
        for definition in class_generator._get_error_class_definitions(
            legacy_classes, module, name
        ):
            definitions[definition.error_origin] = definition
    class_generator._write_shared_errors(
        str(classes), definitions, source_path=legacy_classes
    )
    generated_errors = (classes / "_error.py").read_text(encoding="utf-8")
    class_generator._write_shared_errors(
        str(classes), dict(reversed(list(definitions.items()))), source_path=legacy_classes
    )
    assert (classes / "_error.py").read_text(encoding="utf-8") == generated_errors
    source = Path(MAIN_DIR) / "Functions"
    output = package_root / "Functions_new"
    generate_functions(source, output, classes)
    for module, errors in FUNCTION_ERRORS.items():
        path = source.joinpath(*module.split("."))
        path = path / "__init__.py" if path.is_dir() else path.with_suffix(".py")
        generated = output / path.relative_to(source)
        if module in ("Converter.Utils.ConvertionError", "Converter.Utils.EquivalentError"):
            assert not generated.exists()
            continue
        tree = ast.parse(generated.read_text(encoding="utf-8-sig"))
        assert not ({n.name for n in tree.body if isinstance(n, ast.ClassDef)} & set(errors))

    script = f"""
import pyleecan
pyleecan.__path__.insert(0, {str(package_root)!r})
from pyleecan.Classes_new import _error
from pyleecan.Classes_new._error import FTError, AxisError, NormError, UnitError
from pyleecan.Classes_new._error import GMSHInputError as InputError
from pyleecan.Classes_new._error import PathImportError as ImportError, FileError
from pyleecan.Functions_new.Load.load_json import load_json
from pyleecan.Classes_new._error import (
    DimError, FormatError, LoadMissingFileError, LoadWrongTypeError,
    RetroCompatibilityError,
)
assert FTError is _error.FTError
assert all(issubclass(x, FTError) for x in (AxisError, NormError, UnitError))
assert InputError is _error.GMSHInputError and InputError is not _error.InputError
assert ImportError is _error.PathImportError and ImportError is not _error.PyleecanImportError
assert FileError is _error.FileError
assert LoadMissingFileError is _error.LoadMissingFileError
assert LoadWrongTypeError is _error.LoadWrongTypeError
assert FormatError is _error.FormatError
assert RetroCompatibilityError is _error.RetroCompatibilityError
assert DimError is _error.DimError
try:
    load_json('missing-example.json')
except _error.LoadMissingFileError:
    pass
else:
    raise AssertionError('missing file was not reported')
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("style", ["absolute", "relative"])
def test_generated_classes_redirect_functions_but_defer_load_save(style):
    source = (
        "from pyleecan.Functions.Electrical.dqh_transformation import n2dqh\n"
        "from pyleecan.Functions.load import load_init_dict\n"
        "from pyleecan.Functions.Load.retrocompatibility import convert_init_dict\n"
        "from pyleecan.Functions.save import save\n"
    )
    result = _redirect_experimental_function_imports(source, "pyleecan")
    result = _apply_import_style(result, "pyleecan", style, "Classes_new")
    prefix = "pyleecan." if style == "absolute" else ".."
    assert (
        f"from {prefix}Functions_new.Electrical.dqh_transformation import n2dqh"
        in result
    )
    assert f"from {prefix}Functions.load import load_init_dict" in result
    assert (
        f"from {prefix}Functions.Load.retrocompatibility import convert_init_dict"
        in result
    )
    assert f"from {prefix}Functions.save import save" in result


def test_generated_classes_redirect_dynamic_function_imports():
    source = (
        "module = import_module('pyleecan.Functions.SciDataTool.conversions')\n"
        "other = __import__(f'pyleecan.Functions.Converter.MotorCAD.{name}')\n"
        "load = import_module('pyleecan.Functions.load')\n"
        "message = 'pyleecan.Functions.not_an_import'\n"
    )
    result = _redirect_experimental_function_imports(source, "pyleecan")
    assert "import_module('pyleecan.Functions_new.SciDataTool.conversions')" in result
    assert "__import__(f'pyleecan.Functions_new.Converter.MotorCAD.{name}')" in result
    assert "import_module('pyleecan.Functions.load')" in result
    assert "message = 'pyleecan.Functions.not_an_import'" in result


def test_copied_dqh_checker_accepts_experimental_data():
    from pyleecan.Classes_new.data_1d import Data1D
    from pyleecan.Classes_new.data_time import DataTime
    from pyleecan.Functions_new.Electrical.dqh_transformation import _check_data

    data = DataTime(axes=[Data1D(name="time"), Data1D(name="phase")])
    assert _check_data(data) is None
