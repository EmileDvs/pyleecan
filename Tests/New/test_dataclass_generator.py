"""Tests for the experimental generator's integration with class_generator."""

import ast
import importlib
import os
import pickle
import shutil
import subprocess
import sys
from copy import deepcopy
from dataclasses import dataclass, field, fields, make_dataclass
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import get_type_hints

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New import class_generator
from pyleecan.Generator.read_fct import read_all


@pytest.fixture
def generator_environment(monkeypatch):
    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    gen_dict = read_all(DOC_DIR)
    for name in ("Magnetics", "MagFEMM"):
        gen_dict[name] = deepcopy(gen_dict[name])
        gen_dict[name]["methods"] = []
    return gen_dict


def test_experimental_generator(generator_environment, tmp_path):
    path = class_generator.generate_class(
        generator_environment, "Magnetics", str(tmp_path), )
    first = Path(path).read_text(encoding="utf-8")
    assert Path(path).name == "magnetics.py"
    assert "from pyleecan.Classes_new._pyleecan_class import PyleecanClass" in first

    module = ast.parse(first)
    generated_class = next(
        node for node in module.body if isinstance(node, ast.ClassDef)
    )
    assert generated_class.name == "Magnetics"
    assert isinstance(generated_class.bases[0], ast.Name)
    assert generated_class.bases[0].id == "PyleecanClass"
    assert not any(
        isinstance(node, ast.FunctionDef)
        and node.name in ("_assert_parent_type", "__post_init__")
        for node in generated_class.body
    )

    child_path = class_generator.generate_class(
        generator_environment, "MagFEMM", str(tmp_path), )
    child_source = Path(child_path).read_text(encoding="utf-8")
    assert "from pyleecan.Classes_new.magnetics import Magnetics" in child_source
    child_module = ast.parse(child_source)
    child_class = next(
        node for node in child_module.body if isinstance(node, ast.ClassDef)
    )
    assert child_class.name == "MagFEMM"
    assert isinstance(child_class.bases[0], ast.Name)
    assert child_class.bases[0].id == "Magnetics"


def test_class_generator_rejects_legacy_mode(generator_environment, tmp_path):
    with pytest.raises(TypeError, match="is_new"):
        class_generator.generate_class(
            generator_environment, "Magnetics", str(tmp_path), is_new=False
        )
    assert not list(tmp_path.iterdir())


def test_parent_mapping_uses_root_owners_and_generated_names(generator_environment):
    mapping = class_generator.parent_type_mapping(generator_environment)
    assert mapping[("normalization", "Normalization")] == (("data", "Data"),)
    assert ("data", "Data") in mapping[("data", "Data")]
    assert ("norm_ref", "NormRef") not in mapping


def test_base_is_guarded_and_inherited_post_init_links_children(monkeypatch):
    from pyleecan.Classes_new import _pyleecan_class

    base = _pyleecan_class.PyleecanClass
    with pytest.raises(TypeError, match="PyleecanClass cannot be instantiated directly"):
        base()

    @dataclass(eq=False)
    class Child(base):
        value: int = 0

    @dataclass(eq=False)
    class Owner(base):
        children: list[Child] = field(default_factory=list)

    @dataclass(eq=False)
    class DerivedOwner(Owner):
        extra: int = 0

    monkeypatch.setattr(_pyleecan_class, "PARENT_TYPES", {})
    child = Child(value=7)
    owner = DerivedOwner(children=[child], extra=3)
    assert child.parent is owner
    assert "__post_init__" not in Owner.__dict__
    copied = deepcopy(owner)
    assert copied is not owner
    assert copied.children[0] is not child
    assert copied.children[0].parent is copied


def test_parent_links_on_field_assignment(monkeypatch):
    from pyleecan.Classes_new import _pyleecan_class

    @dataclass(eq=False)
    class Child(_pyleecan_class.PyleecanClass):
        pass

    @dataclass(eq=False)
    class Owner(_pyleecan_class.PyleecanClass):
        child: Child | None = None
        children: dict = field(default_factory=dict)

    monkeypatch.setattr(_pyleecan_class, "PARENT_TYPES", {})
    owner = Owner()
    child = Child()
    owner.child = child
    assert child.parent is owner
    nested = Child()
    owner.children = {"items": [nested]}
    assert nested.parent is owner
    owner.parent = child
    assert owner.parent is child
    assert child.parent is owner


def test_simulation_input_parent_on_assignment():
    from pyleecan.Classes_new.input_current import InputCurrent
    from pyleecan.Classes_new.simulation import Simulation

    simulation = Simulation()
    input_current = InputCurrent()
    simulation.input = input_current
    assert input_current.parent is simulation
    constructed = Simulation(input=InputCurrent())
    assert constructed.input.parent is constructed
    replacement = InputCurrent()
    simulation.input = replacement
    assert replacement.parent is simulation
    simulation.input = None
    assert simulation.input is None


def test_invalid_parent_assignment_does_not_replace_existing_field():
    from pyleecan.Classes_new.data import Data
    from pyleecan.Classes_new.input_current import InputCurrent
    from pyleecan.Classes_new.simulation import Simulation

    simulation = Simulation(input=InputCurrent())
    original = simulation.input
    invalid = Data()
    with pytest.raises(TypeError, match="Data parent"):
        simulation.input = invalid
    assert simulation.input is original
    assert original.parent is simulation
    assert invalid.parent is None


def test_parent_mapping_handles_special_module_and_class_names():
    gen_dict = {
        "Data1D": {"mother": "", "properties": []},
        "Norm_ref": {"mother": "", "properties": [{"type": "Data1D"}]},
        "OPdq": {"mother": "", "properties": [{"type": "Data1D"}]},
        "XOutput": {"mother": "", "properties": [{"type": "Data1D"}]},
    }
    assert class_generator.parent_type_mapping(gen_dict) == {
        ("data_1d", "Data1D"): (
            ("norm_ref", "NormRef"),
            ("op_dq", "OPdq"),
            ("xoutput", "XOutput"),
        )
    }


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_normalization_does_not_import_parent(
    generator_environment, tmp_path, import_style
):
    path = class_generator.generate_class(
        generator_environment,
        "Normalization",
        str(tmp_path),
        import_style=import_style,
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "_assert_parent_type" not in source
    assert "import Data" not in source


def test_shared_parent_validation(monkeypatch):
    from pyleecan.Classes_new import _pyleecan_class

    package = "pyleecan.Classes_new"
    root_module = ModuleType(package + ".test_parent_root")
    owner_module = ModuleType(package + ".test_parent_owner")

    class Root(_pyleecan_class.PyleecanClass):
        def __post_init__(self):
            super().__post_init__()

    class Child(Root):
        pass

    class Owner:
        pass

    class DerivedOwner(Owner):
        pass

    Root.__module__ = root_module.__name__
    Owner.__module__ = owner_module.__name__
    root_module.Root = Root
    owner_module.Owner = Owner
    monkeypatch.setitem(sys.modules, root_module.__name__, root_module)
    monkeypatch.setitem(sys.modules, owner_module.__name__, owner_module)
    monkeypatch.setattr(
        _pyleecan_class,
        "PARENT_TYPES",
        {("test_parent_root", "Root"): (("test_parent_owner", "Owner"),)},
    )
    child = Child()
    child._assert_parent_type(None)
    child._assert_parent_type(DerivedOwner())
    with pytest.raises(TypeError, match="Root parent must be an instance of Owner"):
        child._assert_parent_type(type("Owner", (), {})())
    owner = Owner()
    _pyleecan_class.PyleecanClass._set_parent_links({"a": [child]}, owner)
    assert child.parent is owner
    with pytest.raises(TypeError):
        _pyleecan_class.PyleecanClass._set_parent_links([child], object())
    assert child.parent is owner

    monkeypatch.setattr(_pyleecan_class, "PARENT_TYPES", {})
    child._assert_parent_type(object())
    monkeypatch.setattr(
        _pyleecan_class,
        "PARENT_TYPES",
        {("test_parent_root", "Root"): (("missing_parent_module", "Owner"),)},
    )
    with pytest.raises(ModuleNotFoundError):
        child._assert_parent_type(owner)


def test_normalization_data_parent_link():
    from pyleecan.Classes_new.data import Data
    from pyleecan.Classes_new.norm_vector import NormVector

    normalization = NormVector()
    data = Data(normalizations={"test": normalization})
    assert normalization.parent is data
    for copied in (data.copy(), deepcopy(data), pickle.loads(pickle.dumps(data))):
        assert copied is not data
        assert copied.normalizations["test"] is not normalization
        assert copied.normalizations["test"].parent is copied
    with pytest.raises(TypeError, match="Normalization parent"):
        normalization._assert_parent_type(object())
    data._assert_parent_type(Data())


@pytest.mark.parametrize(
    "imports",
    [
        "from pyleecan.Classes_new.norm_vector import NormVector; "
        "from pyleecan.Classes_new.data import Data; ",
        "from pyleecan.Classes_new.data import Data; "
        "from pyleecan.Classes_new.norm_vector import NormVector; ",
    ],
)
def test_normalization_data_import_in_fresh_process(imports):
    subprocess.run(
        [
            sys.executable,
            "-c",
            imports
            + (
                "n = NormVector(); d = Data(normalizations={'n': n}); "
                "assert n.parent is d"
            ),
        ],
        check=True,
    )


@pytest.mark.parametrize(
    ("class_name", "module_name"),
    [
        ("Magnetics", "magnetics"),
        ("MagFEMM", "mag_femm"),
        ("CondType11", "cond_type_11"),
        ("Data1D", "data_1d"),
        ("LUT", "lut"),
        ("LUTdq", "lut_dq"),
        ("LUTslip", "lut_slip"),
        ("ElecLUTdq", "elec_lut_dq"),
        ("PostLUT", "post_lut"),
        ("LUTdqLUTslip", "lut_dq_lut_slip"),
        ("ScalarProductL2", "scalar_product_l2"),
        ("XOutput", "xoutput"),
        ("Import", "import_"),
        ("OP", "op"),
        ("OPdq", "op_dq"),
        ("OPdqf", "op_dqf"),
        ("OPslip", "op_slip"),
        ("OPMatrix", "op_matrix"),
    ],
)
def test_class_module_name(class_name, module_name):
    assert class_generator.class_module_name(class_name) == module_name


def test_experimental_module_names_are_unambiguous(generator_environment):
    class_generator.validate_class_module_names(generator_environment)
    with pytest.raises(ValueError, match="both map to module"):
        class_generator.validate_class_module_names({"MagFEMM": {}, "MagFemm": {}})


def test_exception_sorting_respects_bases_and_alphabetizes_ready_classes():
    definitions = ast.parse(
        "class ZBase(Exception): pass\n"
        "class AChild(ZBase): pass\n"
        "class CChild(ZBase): pass\n"
        "class BChild(ZBase): pass\n"
    ).body
    expected = ["ZBase", "AChild", "BChild", "CChild"]
    for items in (definitions, list(reversed(definitions))):
        ordered = class_generator._sort_error_class_definitions(items)
        assert [node.name for node in ordered] == expected
        namespace = {}
        exec(
            compile(ast.Module(body=ordered, type_ignores=[]), "<errors>", "exec"),
            namespace,
        )
        assert issubclass(namespace["AChild"], namespace["ZBase"])


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_vendored_class_imports_are_redirected(import_style):
    source = (
        "from pyleecan.Classes._smoot.smoot import MOO as Optimizer\n"
        "from pyleecan.Classes._swat_em import datamodel\n"
        "from pyleecan.Classes._other import untouched\n"
    )
    result = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", {}
    )
    result = class_generator._apply_import_style(
        result, "pyleecan", import_style, "Classes_new"
    )
    prefix = "pyleecan.Classes_new." if import_style == "absolute" else "."
    assert f"from {prefix}_smoot.smoot import MOO as Optimizer" in result
    assert f"from {prefix}_swat_em import datamodel" in result
    assert "Classes._other import untouched" in result


@pytest.mark.parametrize(
    ("class_name", "method_path", "method_name", "package"),
    [
        ("Winding", ("Machine", "Winding"), "comp_connection_mat", "_swat_em"),
        (
            "OptiBayesAlgSmoot",
            ("Optimization", "OptiBayesAlgSmoot"),
            "solve",
            "_smoot.smoot",
        ),
    ],
)
def test_generated_methods_use_vendored_classes(
    generator_environment, tmp_path, class_name, method_path, method_name, package
):
    class_dict = deepcopy(generator_environment[class_name])
    class_dict["methods"] = [method_name]
    methods = tmp_path / "Methods" / Path(*method_path)
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / Path(*method_path) / f"{method_name}.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict[class_name] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        class_name,
        str(output),
        import_style="relative",
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert f"from .{package} import " in source
    assert f"Classes.{package} import " not in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_method_imports_shared_function_error(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["MeshSolution"])
    class_dict["methods"] = ["get_field"]
    methods = tmp_path / "Methods" / "Mesh" / "MeshSolution"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Mesh" / "MeshSolution" / "get_field.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict["MeshSolution"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict, "MeshSolution", str(output),
        import_style=import_style, class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    prefix = "." if import_style == "relative" else "pyleecan.Classes_new."
    assert f"from {prefix}_error import DimError" in source
    assert "import cart2pol, pol2cart" in source


def test_exception_sorting_reports_circular_dependencies():
    definitions = ast.parse(
        "class AError(BError): pass\nclass BError(AError): pass\n"
    ).body
    with pytest.raises(ValueError, match="Circular exception class dependencies"):
        class_generator._sort_error_class_definitions(definitions)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_shared_exceptions_across_partial_generation(
    generator_environment, tmp_path, monkeypatch, import_style
):
    runner = importlib.import_module(
        "pyleecan.Generator.ClassGenerator.New.run_generate_classes"
    )
    package = "test_shared_errors_" + import_style
    root = tmp_path / package
    classes = root / "Classes_new"
    classes.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "Classes").mkdir()
    (classes / "_pyleecan_class.py").write_text(
        "class PyleecanClass:\n    pass\n", encoding="utf-8"
    )
    shared = root / "Methods" / "Slot" / "Shared"
    shared.mkdir(parents=True)
    (shared / "__init__.py").write_text(
        "class SharedError(Exception):\n    pass\n", encoding="utf-8"
    )
    gen_dict = {}
    for name in ("SlotW23", "SlotW24"):
        info = deepcopy(generator_environment[name])
        info.update(mother="", properties=[], constants=[], methods=["check"])
        gen_dict[name] = info
        method_dir = root / "Methods" / "Slot" / name
        method_dir.mkdir(parents=True)
        (method_dir / "check.py").write_text(
            f"from {package}.Methods.Slot.Shared import SharedError\n"
            "class LocalError(SharedError):\n    pass\n"
            "def check(self):\n    raise LocalError('failed')\n",
            encoding="utf-8",
        )
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in gen_dict:
        runner.generate_code(
            str(root), gen_dict, soft_name=package,
            class_list=[name + ".csv"], max_workers=1, import_style=import_style,
        )
    first = importlib.import_module(package + ".Classes_new.slot_w_23")
    second = importlib.import_module(package + ".Classes_new.slot_w_24")
    errors = importlib.import_module(package + ".Classes_new._error")
    assert first.SharedError is second.SharedError is errors.SharedError
    assert not hasattr(first.SlotW23, "SharedError")
    assert not hasattr(first, "LocalError")
    assert first.SlotW23.LocalError is not second.SlotW24.LocalError
    assert issubclass(first.SlotW23.LocalError, errors.SharedError)
    assert issubclass(second.SlotW24.LocalError, errors.SharedError)
    with pytest.raises(errors.SharedError):
        first.SlotW23().check()
    with pytest.raises(errors.SharedError):
        second.SlotW24().check()


def test_same_named_error_sources_raise_conflict(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PATH", str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    )
    root = tmp_path / "source"
    output = root / "Classes_new"
    output.mkdir(parents=True)
    identities = []
    definitions = {}
    for package in ("First", "Second"):
        folder = root / "Methods" / package
        folder.mkdir(parents=True)
        (folder / "__init__.py").write_text(
            "class SameError(Exception):\n    pass\n", encoding="utf-8"
        )
        module = "example.Methods." + package
        identity = ("ImportFrom", 0, module, "SameError", None)
        identities.append(identity)
        definition = class_generator._get_error_class_definitions(
            str(output), module, "SameError"
        )[0]
        definitions[definition.error_origin] = definition

    assert not class_generator._same_error_class_import(
        str(output), *identities
    )
    with pytest.raises(ValueError, match="SameError"):
        class_generator._write_shared_errors(str(output), definitions)
    assert not (output / "_error.py").exists()


def test_real_shared_exception_hierarchy(generator_environment, tmp_path, monkeypatch):
    source = str(Path(MAIN_DIR) / "Classes_new")
    graph = class_generator.get_class_import_graph(
        str(Path(MAIN_DIR) / "Classes"), generator_environment, "pyleecan"
    )
    definitions = class_generator._shared_error_definitions(
        generator_environment, source, "pyleecan", graph
    )
    class_generator._write_shared_errors(str(tmp_path), definitions, source_path=source)
    original = (tmp_path / "_error.py").read_text(encoding="utf-8")
    remaining = {
        node.name: node for node in ast.parse(original).body
        if isinstance(node, ast.ClassDef)
    }
    for definition in [
        node for node in ast.parse(original).body if isinstance(node, ast.ClassDef)
    ]:
        ready = sorted(
            name for name, node in remaining.items()
            if not any(
                isinstance(base, ast.Name) and base.id in remaining
                for base in node.bases
            )
        )
        assert definition.name == ready[0]
        del remaining[definition.name]
    class_generator._write_shared_errors(
        str(tmp_path), dict(reversed(list(definitions.items()))), source_path=source
    )
    assert (tmp_path / "_error.py").read_text(encoding="utf-8") == original
    spec = importlib.util.spec_from_file_location("real_shared_errors", tmp_path / "_error.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    assert not hasattr(module, "ERROR_TYPES")
    assert not hasattr(module, "ImportError")
    assert issubclass(module.AxisError, module.FTError)
    assert module.GMSHInputError is not module.InputError
    assert module.PathImportError is not module.PyleecanImportError
    assert issubclass(module.RetroCompatibilityError, Exception)
    assert issubclass(module.PyleecanImportError, Exception)
    assert pickle.loads(pickle.dumps(module.MachineCheckError("test"))).__class__ is (
        module.MachineCheckError
    )
    assert issubclass(module.SlotCheckError, module.LaminationCheckError)
    assert issubclass(module.LaminationCheckError, module.MachineCheckError)


def test_check_exceptions_are_shared_and_preserve_validation_behavior(tmp_path):
    from pyleecan.Classes_new import _check, _error

    definitions = class_generator._check_error_definitions()
    class_generator._write_shared_errors(str(tmp_path), {})
    tree = ast.parse((tmp_path / "_error.py").read_text(encoding="utf-8"))
    generated = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    assert set(definitions) <= set(generated)
    for name, definition in definitions.items():
        assert ast.dump(generated[name]) == ast.dump(definition)
    assert not any(
        isinstance(node, ast.ClassDef) and node.name in definitions
        for node in ast.parse(Path(_check.__file__).read_text(encoding="utf-8")).body
    )
    for name in definitions:
        instance = getattr(_error, name)("test")
        assert type(pickle.loads(pickle.dumps(instance))) is type(instance)
    assert issubclass(_error.CheckTypeError, _error.CheckError)
    assert issubclass(_error.CheckMinError, _error.CheckError)
    assert issubclass(_error.CheckMaxError, _error.CheckError)
    with pytest.raises(_error.CheckTypeError):
        _check.check_var("value", "wrong", "int")
    with pytest.raises(_error.CheckMinError):
        _check.check_var("value", -1, "int", Vmin=0)
    with pytest.raises(_error.CheckMaxError):
        _check.check_var("value", 2, "int", Vmax=1)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
@pytest.mark.parametrize("class_name", ["DataKeeper", "ParamExplorer"])
def test_generated_check_error_imports(
    generator_environment, tmp_path, class_name, import_style
):
    methods = tmp_path / "Methods" / "Simulation" / class_name
    shutil.copytree(Path(MAIN_DIR) / "Methods" / "Simulation" / class_name, methods)
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        generator_environment, class_name, str(output), import_style=import_style, class_import_graph={}, shared_error_definitions={},
    )
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    imports = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and any(alias.name == "CheckTypeError" for alias in node.names)
    ]
    assert len(imports) == 1
    assert (imports[0].level, imports[0].module) == (
        (1, "_error") if import_style == "relative"
        else (0, "pyleecan.Classes_new._error")
    )


def test_check_import_redirect_splits_errors_and_helpers():
    source = (
        "from pyleecan.Classes._check import check_var as validate, "
        "CheckTypeError as TypeErrorAlias\n"
    )
    result = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", {}
    )
    tree = ast.parse(result)
    assert [
        (node.module, [(alias.name, alias.asname) for alias in node.names])
        for node in tree.body
    ] == [
        ("pyleecan.Classes_new._error", [("CheckTypeError", "TypeErrorAlias")]),
        ("pyleecan.Classes_new._check", [("check_var", "validate")]),
    ]


def test_current_generated_import_error_uses_shared_class():
    from pyleecan.Classes_new._error import PyleecanImportError
    from pyleecan.Classes_new.import_gen_vect_lin import ImportError, ImportGenVectLin

    assert ImportError is PyleecanImportError
    assert not hasattr(ImportGenVectLin, "ImportError")
    with pytest.raises(PyleecanImportError, match="Start must not be None"):
        ImportGenVectLin(start=None).check()


def test_generated_hole_m50_local_errors_are_usable(generator_environment, tmp_path):
    root = tmp_path
    methods = root / "Methods"
    for package in (("Slot", "HoleM50"), ("Slot", "Slot"), ("Machine", "Lamination")):
        shutil.copytree(
            Path(MAIN_DIR, "Methods", *package), methods.joinpath(*package)
        )
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Machine" / "__init__.py",
        methods / "Machine" / "__init__.py",
    )
    output = root / "Classes_new"
    output.mkdir()
    definitions = class_generator._get_error_class_definitions(
        str(output), "pyleecan.Methods.Slot.Slot", "SlotCheckError"
    )
    shared = {definition.error_origin: definition for definition in definitions}
    info = deepcopy(generator_environment["HoleM50"])
    info.update(mother="", properties=[], constants=[], methods=["check"])
    gen_dict = dict(generator_environment)
    gen_dict["HoleM50"] = info
    path = class_generator.generate_class(
        gen_dict, "HoleM50", str(output), import_style="relative",
        class_import_graph={}, shared_error_definitions=shared,
    )
    source = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert "from ._error import SlotCheckError" in source
    assert "_shared_" not in source
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    local_names = {node.name for node in cls.body if isinstance(node, ast.ClassDef)}
    assert "S50_NoneError" in local_names
    assert "SlotCheckError" not in local_names
    assert "raise self.S50_NoneError" in source
    assert not any(isinstance(node, ast.Assign) for node in tree.body)

    cls.decorator_list = []
    cls.bases = []
    from pyleecan.Classes_new._error import SlotCheckError

    namespace = {"SlotCheckError": SlotCheckError}
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
            str(path),
            "exec",
        ),
        namespace,
    )
    hole_class = namespace["HoleM50"]
    hole = hole_class()
    hole.get_Rext = lambda: 1
    hole.W0 = None
    with pytest.raises(hole_class.S50_NoneError, match="W0"):
        hole.check()


def test_local_error_references_use_self_only_in_instance_methods():
    source = (
        "def check(self):\n"
        "    raise LocalError('instance')\n"
        "\n"
        "@staticmethod\n"
        "def helper():\n"
        "    raise LocalError('static')\n"
        "\n"
        "def other():\n"
        "    raise LocalError('no instance')\n"
        "\n"
        "def rebound(self):\n"
        "    self = None\n"
        "    raise LocalError('rebound')\n"
    )
    result = class_generator._qualify_local_errors(source, {"LocalError"}, "Example")
    assert "raise self.LocalError('instance')" in result
    assert "raise Example.LocalError('static')" in result
    assert "raise Example.LocalError('no instance')" in result
    assert "raise Example.LocalError('rebound')" in result

    namespace = {}
    exec(
        "class Example:\n"
        "    class LocalError(Exception):\n"
        "        pass\n"
        + "\n".join("    " + line for line in result.splitlines()),
        namespace,
    )
    example = namespace["Example"]
    for call in (example().check, example.helper, example.other, example().rebound):
        with pytest.raises(example.LocalError):
            call()

    class Derived(example):
        class LocalError(Exception):
            pass

    with pytest.raises(Derived.LocalError):
        Derived().check()


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_slot_w23_errors_have_deterministic_order(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["SlotW23"])
    class_dict["methods"] = ["check"]
    methods = tmp_path / "Methods" / "Slot"
    methods.mkdir(parents=True)
    for name in ("SlotW23", "Slot", "Lamination", "Machine"):
        source = Path(MAIN_DIR) / "Methods" / "Slot" / name
        if source.is_dir():
            shutil.copytree(source, methods / name)
    gen_dict = dict(generator_environment)
    gen_dict["SlotW23"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "SlotW23",
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    names = [node.name for node in cls.body if isinstance(node, ast.ClassDef)]
    assert names.index("S23_H1rCheckError") < names.index("S23_W01CheckError")
    assert names.index("SlotCheckError") < names.index("S23_H1rCheckError")
    aliases = [
        node.targets[0].id
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in names
    ]
    assert aliases == []


@pytest.mark.parametrize(
    ("prop_type", "value"),
    [
        ("{Normalization}", {}),
        ("[Normalization]", []),
        ("{[Normalization]}", {"axis": [1]}),
        ("[Normalization]", [{"value": 1}]),
        ("dict", {"key": [1]}),
        ("list", [[1]]),
    ],
)
def test_mutable_defaults_are_independent(prop_type, value):
    expression = class_generator._field_default({"type": prop_type, "value": value})
    field_value = eval(
        expression, {"field": field, "partial": partial, "deepcopy": deepcopy}
    )
    cls = make_dataclass("Example", [("value", object, field_value)])
    first, second = cls(), cls()
    assert first.value == value
    assert second.value == value
    assert first.value is not second.value
    if value:
        if isinstance(value, dict):
            first.value[next(iter(value))].append(2)
        else:
            first.value[0].clear()
        assert second.value == value


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_data_normalizations_uses_default_factory(
    generator_environment, tmp_path, import_style
):
    gen_dict = dict(generator_environment)
    gen_dict["Data"] = deepcopy(gen_dict["Data"])
    gen_dict["Data"]["methods"] = []
    path = class_generator.generate_class(
        gen_dict,
        "Data",
        str(tmp_path),
        import_style=import_style,
        class_import_graph={},
    )
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    data_class = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    assignment = next(
        node
        for node in data_class.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "normalizations"
    )
    assert ast.unparse(assignment.value) == "field(default_factory=dict)"
    field_value = eval(
        compile(ast.Expression(assignment.value), str(path), "eval"), {"field": field}
    )
    cls = make_dataclass("DataDefaults", [("normalizations", dict, field_value)])
    first, second = cls(), cls()
    first.normalizations["test"] = 1
    assert second.normalizations == {}


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
@pytest.mark.parametrize(
    ("class_name", "factory_names"),
    [
        ("ImportData", ("axes", "normalizations", "symmetries")),
        ("SolutionMat", ("axis_name", "axis_size")),
    ],
)
def test_field_attribute_does_not_shadow_factory(
    generator_environment, tmp_path, import_style, class_name, factory_names
):
    gen_dict = dict(generator_environment)
    gen_dict[class_name] = deepcopy(gen_dict[class_name])
    gen_dict[class_name]["methods"] = []
    path = class_generator.generate_class(
        gen_dict,
        class_name,
        str(tmp_path),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "field as dataclass_field" in source
    tree = ast.parse(source)
    definition = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    assignments = {
        node.target.id: node
        for node in definition.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    for name in factory_names:
        assert ast.unparse(assignments[name].value).startswith("dataclass_field(")
    namespace = {"dataclass_field": field}
    for node in definition.body:
        if isinstance(node, ast.AnnAssign):
            node.annotation = ast.Name(id="object", ctx=ast.Load())
    definition.decorator_list = []
    definition.bases = []
    definition.body = [
        node
        for node in definition.body
        if isinstance(node, ast.AnnAssign)
    ]
    exec(
        compile(ast.fix_missing_locations(ast.Module(body=[definition], type_ignores=[])),
                str(path), "exec"),
        namespace,
    )
    from dataclasses import dataclass

    cls = dataclass(namespace[class_name])
    first, second = cls(), cls()
    assert first.field is None
    for name in factory_names:
        first_value, second_value = getattr(first, name), getattr(second, name)
        assert first_value is not second_value
        if isinstance(first_value, list):
            first_value.append(1)
            assert second_value == []
        else:
            first_value["x"] = 1
            assert second_value == {}


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_self_imports_and_recursive_types(
    generator_environment, tmp_path, monkeypatch, import_style
):
    class_dict = deepcopy(generator_environment["Output"])
    class_dict["mother"] = ""
    class_dict["methods"] = ["comp_axes"]
    recursive_prop = deepcopy(generator_environment["VarSimu"]["properties"][0])
    recursive_prop.update({"name": "child", "type": "Output", "value": None})
    recursive_list = deepcopy(generator_environment["ImportData"]["properties"][0])
    recursive_list.update({"name": "children", "type": "[Output]", "value": None})
    class_dict["properties"] = [recursive_prop, recursive_list]
    owner = deepcopy(generator_environment["OutElec"])
    owner["mother"] = "Output"
    owner["properties"] = [recursive_prop]
    gen_dict = {"Output": class_dict, "OutElec": owner}

    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Output" / "Output"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from pyleecan.Classes.Output import Output\n"
        "def comp_axes(self, other: Output = None) -> Output:\n"
        "    return Output\n",
        encoding="utf-8",
    )
    path = class_generator.generate_class(
        gen_dict,
        "Output",
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "from .output import Output" not in source
    assert "from pyleecan.Classes_new.output import Output" not in source
    assert "from __future__ import annotations" in source
    assert "child: Output | None = field(" in source
    assert "children: list[Output] | None = None" in source
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    annotations = {
        node.target.id: node.annotation
        for node in cls.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert not isinstance(annotations["child"], ast.Constant)
    assert not isinstance(annotations["children"], ast.Constant)

    name = "pyleecan.Classes_new.test_recursive_output"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    assert get_type_hints(module.Output)["child"] == module.Output | None
    assert get_type_hints(module.Output)["children"] == list[module.Output] | None
    assert get_type_hints(module.Output.comp_axes)["other"] is module.Output
    assert get_type_hints(module.Output.comp_axes)["return"] is module.Output
    instance = module.Output()
    assert instance.comp_axes() is module.Output
    from pyleecan.Classes_new import _pyleecan_class

    monkeypatch.setattr(
        _pyleecan_class,
        "PARENT_TYPES",
        {("test_recursive_output", "Output"): (("test_recursive_output", "Output"),)},
    )
    instance._assert_parent_type(module.Output())
    with pytest.raises(TypeError):
        instance._assert_parent_type(object())
    assert module.Output.from_dict({"child": None, "children": None}).child is None


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_var_simu_self_annotation(
    generator_environment, tmp_path, monkeypatch, import_style
):
    info = deepcopy(generator_environment["VarSimu"])
    info.update(
        mother="",
        constants=[],
        methods=[],
        properties=[prop for prop in info["properties"] if prop["name"] == "var_simu"],
    )
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        {"VarSimu": info},
        "VarSimu",
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "from __future__ import annotations" in source
    assert "var_simu: VarSimu | None = field(" in source
    name = "pyleecan.Classes_new.test_recursive_var_simu"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    assert get_type_hints(module.VarSimu)["var_simu"] == module.VarSimu | None
    assert module.VarSimu.from_dict({"var_simu": None}).var_simu is None


def test_self_module_imports_preserve_other_symbols():
    source = (
        "from pyleecan.Classes_new.example import Example, SHARED, external\n"
        "SHARED = 1\n"
        "class Example:\n"
        "    pass\n"
    )
    result = class_generator._remove_experimental_self_imports(
        source, "pyleecan", "Example", "example"
    )
    assert "from pyleecan.Classes_new.example import external" in result
    assert "SHARED = 1" in result


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_domain_module_names_in_generated_classes(
    generator_environment, tmp_path, import_style
):
    names = {
        "Data1D": "data_1d",
        "DataTime": "data_time",
        "ElecLUTdq": "elec_lut_dq",
        "LUTdq": "lut_dq",
        "LUTslip": "lut_slip",
        "ScalarProductL2": "scalar_product_l2",
        "XOutput": "xoutput",
    }
    gen_dict = dict(generator_environment)
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "SciDataTool" / "DataTime"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "SciDataTool" / "DataTime" / "time_to_freq.py",
        methods,
    )
    for name, module in names.items():
        gen_dict[name] = deepcopy(gen_dict[name])
        gen_dict[name]["methods"] = ["time_to_freq"] if name == "DataTime" else []
        path = class_generator.generate_class(
            gen_dict,
            name,
            str(output),
            import_style=import_style,
            class_import_graph={},
        )
        assert Path(path).name == module + ".py"

    data_time = (output / "data_time.py").read_text(encoding="utf-8")
    expected = (
        "from .data_1d import Data1D"
        if import_style == "relative"
        else "from pyleecan.Classes_new.data_1d import Data1D"
    )
    assert expected in data_time

    source = (
        "\n".join(f"from pyleecan.Classes.{name} import {name}" for name in names)
        + "\n"
    )
    transformed = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", gen_dict
    )
    transformed = class_generator._apply_import_style(
        transformed, "pyleecan", import_style, "Classes_new"
    )
    for name, module in names.items():
        prefix = "." if import_style == "relative" else "pyleecan.Classes_new."
        assert f"from {prefix}{module} import {name}" in transformed


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_operating_point_module_names(
    generator_environment, tmp_path, import_style
):
    names = ("OP", "OPdq", "OPdqf", "OPslip")
    gen_dict = {name: deepcopy(generator_environment[name]) for name in names}
    for class_dict in gen_dict.values():
        class_dict["methods"] = []
        class_dict["properties"] = []
    for name in names:
        path = class_generator.generate_class(
            gen_dict,
            name,
            str(tmp_path),
            import_style=import_style,
            class_import_graph={},
        )
        assert Path(path).name == class_generator.class_module_name(name) + ".py"
    source = (tmp_path / "op_dqf.py").read_text(encoding="utf-8")
    expected = (
        "from .op_dq import OPdq"
        if import_style == "relative"
        else "from pyleecan.Classes_new.op_dq import OPdq"
    )
    assert expected in source
    assert not list(tmp_path.glob("o_p*.py"))


@pytest.mark.parametrize(
    ("import_style", "machine_import", "femm_import", "package_import"),
    [
        (
            "relative",
            "from .machine import ARC_NPOINT_D as POINTS",
            "from .mag_femm import MagFEMM as Model",
            "from ._error import ParentMissingError as Missing",
        ),
        (
            "absolute",
            "from pyleecan.Classes_new.machine import ARC_NPOINT_D as POINTS",
            "from pyleecan.Classes_new.mag_femm import MagFEMM as Model",
            "from pyleecan.Classes_new._error import ParentMissingError as Missing",
        ),
    ],
)
def test_experimental_class_import_redirect(
    import_style, machine_import, femm_import, package_import
):
    source = (
        "from pyleecan.Classes.Machine import ARC_NPOINT_D as POINTS\n"
        "from pyleecan.Classes._check import check_var as validate\n"
        "from pyleecan.Classes._FEMMHandler import _FEMMHandler as Handler\n"
        "from pyleecan.Classes import ParentMissingError as Missing, get_class_dict, unknown\n"
        "from other.Classes.Machine import Machine\n"
        "def method():\n"
        "    from pyleecan.Classes.MagFEMM import MagFEMM as Model\n"
        "    return POINTS, Model\n"
    )
    transformed = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", {"Machine": {}, "MagFEMM": {}}
    )
    transformed = class_generator._apply_import_style(
        transformed, "pyleecan", import_style, "Classes_new"
    )
    assert machine_import in transformed
    assert femm_import in transformed
    if import_style == "relative":
        assert "from ._check import check_var as validate" in transformed
        assert "from ._femm_handler import _FEMMHandler as Handler" in transformed
    else:
        assert "from pyleecan.Classes_new._check import check_var as validate" in transformed
        assert (
            "from pyleecan.Classes_new._femm_handler import _FEMMHandler as Handler"
            in transformed
        )
    assert package_import in transformed
    assert "from pyleecan.Classes import unknown" in transformed or (
        import_style == "relative" and "from ..Classes import unknown" in transformed
    )
    assert "from other.Classes.Machine import Machine" in transformed


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_femm_handler_import(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["MagFEMM"])
    class_dict["methods"] = ["comp_flux_airgap"]
    methods = tmp_path / "Methods" / "Simulation" / "MagFEMM"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "MagFEMM" / "comp_flux_airgap.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict["MagFEMM"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "MagFEMM",
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from ._femm_handler import _FEMMHandler"
        if import_style == "relative"
        else "from pyleecan.Classes_new._femm_handler import _FEMMHandler"
    )
    assert expected in source
    assert "_FEMMHandler()" in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_method_uses_package_exception(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["MagElmer"])
    class_dict["methods"] = ["solve_FEA"]
    methods = tmp_path / "Methods" / "Simulation" / "MagElmer"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "MagElmer" / "solve_FEA.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict["MagElmer"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "MagElmer",
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from ._error import NotImplementedYetError"
        if import_style == "relative"
        else "from pyleecan.Classes_new._error import NotImplementedYetError"
    )
    assert expected in source
    assert "raise NotImplementedYetError(" in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_var_simu_elec_lut_import_is_local(
    generator_environment, tmp_path, monkeypatch, import_style
):
    root = tmp_path
    methods = root / "Methods" / "Simulation" / "VarSimu"
    methods.mkdir(parents=True)
    shutil.copytree(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "VarSimu",
        methods,
        dirs_exist_ok=True,
    )
    info = deepcopy(generator_environment["VarSimu"])
    info["methods"] = ["set_reused_data"]
    gen_dict = dict(generator_environment)
    gen_dict["VarSimu"] = info
    output = root / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "VarSimu",
        str(output),
        import_style=import_style,
        class_import_graph={},
        shared_error_definitions={},
    )
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    assert any(
        isinstance(node, ast.ImportFrom)
        and (node.level, node.module) == (
            (1, "_import") if import_style == "relative"
            else (0, "pyleecan.Classes_new._import")
        )
        and any(alias.name == "import_class" and alias.asname is None for alias in node.names)
        for node in tree.body
    )
    assert not any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "ElecLUTdq" for alias in node.names)
        for node in tree.body
    )
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(
        node for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "set_reused_data"
    )
    assignment = next(
        node for node in method.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "ElecLUTdq"
                for target in node.targets)
    )
    assert ast.unparse(assignment.value) == "import_class('ElecLUTdq')"

    import types

    elec_module = types.ModuleType("pyleecan.Classes_new.elec_lut_dq")
    elec_module.ElecLUTdq = type("ElecLUTdq", (), {})
    monkeypatch.setitem(sys.modules, elec_module.__name__, elec_module)
    method.decorator_list = []
    namespace = {
        "MagFEMM": type("MagFEMM", (), {}),
        "import_class": lambda name: getattr(elec_module, name),
    }
    exec(
        compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                str(path), "exec"),
        namespace,
    )
    target = elec_module.ElecLUTdq()
    reference = object()
    simulation = types.SimpleNamespace(layer=1, mag=None, elec=target)
    result = types.SimpleNamespace(
        simu=types.SimpleNamespace(elec=types.SimpleNamespace(LUT_enforced=reference))
    )
    instance = types.SimpleNamespace(is_reuse_femm_file=False, is_reuse_LUT=True)
    namespace["set_reused_data"](instance, simulation, result, is_log=False)
    assert target.LUT_enforced is reference


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
@pytest.mark.parametrize(
    "class_name,method_name,method_folder,expected",
    [
        ("MeshMat", "convert", "Mesh", {"MeshVTK": "mesh_vtk"}),
        ("MeshVTK", "convert", "Mesh", {"MeshMat": "mesh_mat"}),
        ("Simulation", "run", "Simulation", {"XOutput": "xoutput", "Output": "output"}),
    ],
)
def test_method_local_classes_use_import_class(
    generator_environment, tmp_path, import_style, class_name, method_name,
    method_folder, expected,
):
    methods = tmp_path / "Methods" / method_folder / class_name
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / method_folder / class_name / (method_name + ".py"),
        methods,
    )
    info = deepcopy(generator_environment[class_name])
    info["methods"] = [method_name]
    gen_dict = dict(generator_environment)
    gen_dict[class_name] = info
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict, class_name, str(output), import_style=import_style, class_import_graph={}, shared_error_definitions={},
    )
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(
        node for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == method_name
    )
    for imported_class in expected:
        assignments = [
            node for node in ast.walk(method)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == imported_class
                for target in node.targets
            )
        ]
        assert len(assignments) == 1
        call = assignments[0].value
        assert isinstance(call, ast.Call)
        assert [arg.value for arg in call.args] == [imported_class]
        assert not call.keywords
        assert not any(
            isinstance(node, ast.ImportFrom)
            and any(alias.name == imported_class for alias in node.names)
            for node in ast.walk(method)
        )




@pytest.mark.parametrize("import_style", ["absolute", "relative"])
@pytest.mark.parametrize(
    ("class_name", "owner", "constant", "value"),
    [
        ("Arc1", "Arc", "ARC_NPOINT_D", 99),
        ("Arc2", "Arc", "ARC_NPOINT_D", 99),
        ("Arc3", "Arc", "ARC_NPOINT_D", 99),
        ("Segment", "Line", "LINE_NPOINT_D", 1),
    ],
)
def test_experimental_geometry_constant_import(
    generator_environment, tmp_path, monkeypatch, import_style,
    class_name, owner, constant, value,
):
    class_dict = deepcopy(generator_environment[class_name])
    class_dict["methods"] = ["discretize"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Geometry" / class_name
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Geometry" / class_name / "discretize.py", methods
    )
    gen_dict = dict(generator_environment)
    gen_dict[class_name] = class_dict
    path = class_generator.generate_class(
        gen_dict,
        class_name,
        str(output),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        f"from .{owner.lower()} import {owner}"
        if import_style == "relative"
        else f"from pyleecan.Classes_new.{owner.lower()} import {owner}"
    )
    assert expected in source
    assert f"nb_point={owner}.{constant}" in source
    assert f"import {constant}" not in source
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    method = next(
        node for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "discretize"
    )
    module = ast.Module(body=[method], type_ignores=[])
    namespace = {owner: type(owner, (), {constant: value})}
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    assert namespace["discretize"].__defaults__ == (value,)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_property_types_import_new_modules(
    generator_environment, tmp_path, import_style
):
    gen_dict = dict(generator_environment)
    gen_dict["Machine"] = deepcopy(gen_dict["Machine"])
    gen_dict["Machine"]["methods"] = []
    path = class_generator.generate_class(
        gen_dict,
        "Machine",
        str(tmp_path),
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from .frame import Frame"
        if import_style == "relative"
        else "from pyleecan.Classes_new.frame import Frame"
    )
    assert expected in source
    assert "Classes.Frame import Frame" not in source




@pytest.mark.parametrize(
    ("class_name", "module_constants", "class_constants"),
    [
        ("Machine", {}, {}),
        ("Arc", {}, {"ARC_NPOINT_D": 99}),
        ("Line", {}, {"LINE_NPOINT_D": 1}),
        (
            "Skew",
            {
                "TYPE_SKEW_LIST": [
                    "linear",
                    "vshape",
                    "zig-zag",
                    "user-defined",
                    "function",
                ]
            },
            {},
        ),
        ("Input", {"ROT_DIR_REF": -1, "CURRENT_DIR_REF": -1, "PHASE_DIR_REF": -1}, {}),
        (
            "SolverInputFile",
            {"WHITESPACE": " ", "INDENT": "  "},
            {"WHITESPACE": " ", "COMMENT": "! ", "MESH_FILE": "Mesh"},
        ),
    ],
)
@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_module_and_class_constants(
    generator_environment,
    tmp_path,
    monkeypatch,
    class_name,
    module_constants,
    class_constants,
    import_style,
):
    class_dict = deepcopy(generator_environment[class_name])
    class_dict["mother"] = ""
    class_dict["properties"] = []
    class_dict["methods"] = []
    class_dict["constants"] = [{"name": "INNER_TEST_CONSTANT", "value": "42"}]
    path = class_generator.generate_class(
        {class_name: class_dict},
        class_name,
        str(tmp_path),
        import_style=import_style,
        class_import_graph={},
    )
    module_name = (
        "pyleecan.Classes_new.test_constants_"
        + class_generator.class_module_name(class_name)
    )
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    generated_class = getattr(module, class_name)
    imported_module = __import__(module_name, fromlist=list(module_constants))
    for name, value in module_constants.items():
        assert getattr(imported_module, name) == value
        if name not in class_constants:
            assert name not in generated_class.__dict__
    for name, value in class_constants.items():
        assert generated_class.__dict__[name] == value
    if class_name == "Machine":
        assert not hasattr(module, "ARC_NPOINT_D")
        assert not hasattr(module, "LINE_NPOINT_D")
        assert not hasattr(generated_class, "ARC_NPOINT_D")
        assert not hasattr(generated_class, "LINE_NPOINT_D")
    assert generated_class.INNER_TEST_CONSTANT == 42
    assert "INNER_TEST_CONSTANT" not in module.__dict__
    assert "INNER_TEST_CONSTANT" not in {
        field.name for field in fields(generated_class)
    }


def test_experimental_method_uses_exported_module_constant(
    generator_environment, tmp_path, monkeypatch
):
    class_dict = deepcopy(generator_environment["Skew"])
    class_dict["mother"] = ""
    class_dict["properties"] = []
    class_dict["methods"] = ["comp_axes"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Machine" / "Skew"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from pyleecan.Methods.Machine.Skew import TYPE_SKEW_LIST\n"
        "def comp_axes(self, value=TYPE_SKEW_LIST):\n"
        "    return value, TYPE_SKEW_LIST\n",
        encoding="utf-8",
    )
    path = class_generator.generate_class(
        {"Skew": class_dict},
        "Skew",
        str(output),
        class_import_graph={},
    )
    name = "pyleecan.Classes_new.test_constants_method"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    values = ["linear", "vshape", "zig-zag", "user-defined", "function"]
    assert module.Skew().comp_axes() == (values, values)
    assert module.Skew().comp_axes(3) == (3, values)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_machine_method_uses_geometry_constant(
    generator_environment, tmp_path, import_style
):
    info = deepcopy(generator_environment["Machine"])
    info.update(mother="", properties=[], constants=[], methods=["comp_axes"])
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Machine" / "Machine"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from pyleecan.Methods.Machine import ARC_NPOINT_D as POINTS\n"
        "def comp_axes(self, count=POINTS):\n"
        "    return count, POINTS\n",
        encoding="utf-8",
    )
    path = class_generator.generate_class(
        {"Machine": info, "Arc": generator_environment["Arc"]},
        "Machine", str(output), import_style=import_style,
        class_import_graph={}, shared_error_definitions={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "count=Arc.ARC_NPOINT_D" in source
    assert "return count, Arc.ARC_NPOINT_D" in source
    assert "from .machine import" not in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_geometry_constant_defaults_at_runtime(
    generator_environment, tmp_path, monkeypatch, import_style
):
    package = "geometry_constants_" + import_style
    root = tmp_path / package
    output = root / "Classes_new"
    output.mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (output / "__init__.py").write_text("", encoding="utf-8")
    (output / "_pyleecan_class.py").write_text(
        "class PyleecanClass:\n    pass\n", encoding="utf-8"
    )
    gen_dict = {}
    for name in ("Line", "Arc", "Arc1", "Arc2", "Arc3", "Segment"):
        info = deepcopy(generator_environment[name])
        info.update(properties=[], constants=[], methods=[])
        if name == "Line":
            info["mother"] = ""
        if name in ("Arc1", "Arc2", "Arc3", "Segment"):
            info["methods"] = ["discretize"]
            destination = root / "Methods" / "Geometry" / name
            destination.mkdir(parents=True)
            shutil.copy2(
                Path(MAIN_DIR) / "Methods" / "Geometry" / name / "discretize.py",
                destination,
            )
            shutil.copy2(
                Path(MAIN_DIR) / "Methods" / "Geometry" / name / "__init__.py",
                destination,
            )
        gen_dict[name] = info
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in gen_dict:
        class_generator.generate_class(
            gen_dict, name, str(output), soft_name=package, import_style=import_style, class_import_graph={},
            shared_error_definitions={},
        )
    line = importlib.import_module(package + ".Classes_new.line").Line
    arc = importlib.import_module(package + ".Classes_new.arc").Arc
    assert line.LINE_NPOINT_D == 1
    assert arc.ARC_NPOINT_D == 99
    for name in ("Arc1", "Arc2", "Arc3", "Segment"):
        module_name = class_generator.class_module_name(name)
        cls = getattr(
            importlib.import_module(package + ".Classes_new." + module_name), name
        )
        assert cls.discretize.__defaults__ == ((1 if name == "Segment" else 99),)
    assert package + ".Classes_new.machine" not in sys.modules


def test_ruff_uses_utf8_for_captured_text(tmp_path, monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command, 0, stdout=kwargs.get("input", ""), stderr=""
        )

    monkeypatch.setattr(class_generator.subprocess, "run", run)
    source = 'from pyleecan.Classes.Magnetics import Magnetics\n\nclass Sample:\n    """Unicode \uff1a"""\n'
    path = str(tmp_path / "sample.py")
    organized = class_generator._organize_header_imports(source, "Sample", path)
    regrouped = class_generator._regroup_pyleecan_imports(organized, "Sample", path)
    assert "\uff1a" in class_generator._format_source_with_ruff(regrouped, path)
    assert len(calls) == 4
    assert all(kwargs["encoding"] == "utf-8" for _, kwargs in calls)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_generated_inheritance_imports(
    generator_environment, tmp_path, monkeypatch, import_style
):
    import pyleecan.Classes_new
    from pyleecan.Classes_new._pyleecan_class import PyleecanClass

    output_dir = tmp_path / "Classes_new"
    output_dir.mkdir()
    methods_dir = tmp_path / "Methods" / "Simulation" / "Magnetics"
    methods_dir.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "Magnetics" / "get_slice_model.py",
        methods_dir / "get_slice_model.py",
    )
    gen_dict = {
        name: deepcopy(generator_environment[name])
        for name in ("Magnetics", "MagFEMM", "SliceModel")
    }
    for class_dict in gen_dict.values():
        class_dict["methods"] = []
        class_dict["properties"] = []
    gen_dict["Magnetics"]["methods"] = ["get_slice_model"]
    monkeypatch.setattr(
        pyleecan.Classes_new,
        "__path__",
        [str(output_dir), *pyleecan.Classes_new.__path__],
    )
    for name in ("magnetics", "mag_femm", "slice_model"):
        monkeypatch.delitem(sys.modules, f"pyleecan.Classes_new.{name}", raising=False)
    for name in ("SliceModel", "Magnetics", "MagFEMM"):
        class_generator.generate_class(
            gen_dict,
            name,
            str(output_dir),
            import_style=import_style,
            class_import_graph={},
        )
    importlib.invalidate_caches()
    try:
        parent = importlib.import_module("pyleecan.Classes_new.magnetics")
        child = importlib.import_module("pyleecan.Classes_new.mag_femm")
        assert issubclass(child.MagFEMM, parent.Magnetics)
        assert issubclass(parent.Magnetics, PyleecanClass)
        assert parent.SliceModel.__module__ == "pyleecan.Classes_new.slice_model"
        assert hasattr(parent.Magnetics, "get_slice_model")
        instance = child.MagFEMM()
        assert instance.parent is None
    finally:
        sys.modules.pop("pyleecan.Classes_new.mag_femm", None)
        sys.modules.pop("pyleecan.Classes_new.magnetics", None)
        sys.modules.pop("pyleecan.Classes_new.slice_model", None)


def test_experimental_custom_output_name(generator_environment, tmp_path, monkeypatch):
    def unexpected_graph_lookup(*args):
        raise AssertionError("A supplied import graph must not be recomputed")

    monkeypatch.setattr(
        class_generator, "get_class_import_graph", unexpected_graph_lookup
    )
    path = class_generator.generate_class(
        generator_environment,
        "Magnetics",
        str(tmp_path),
        output_name="custom",
        class_import_graph={},
    )
    assert Path(path).name == "custom.py"
    module = ast.parse(Path(path).read_text(encoding="utf-8"))
    assert any(
        isinstance(node, ast.ClassDef) and node.name == "Magnetics"
        for node in module.body
    )
