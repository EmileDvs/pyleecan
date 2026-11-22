"""Step 12: the final code in Methods_new (no legacy class loader or import)."""

from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _drop_guarded_header_duplicates,
    _has_method_body_import_guard,
    _static_local_class_imports,
)
from pyleecan.Generator.ClassGenerator.New.modernize import LOCAL_IMPORT_GUARD
from pyleecan.Generator.read_fct import read_all
from pyleecan.definitions import DOC_DIR

GEN_DICT = read_all(DOC_DIR)
LOADER = "from pyleecan.Classes_new._import import import_class\n"


def test_static_imports_with_guard_comment():
    source = LOADER + (
        "def run(self):\n"
        '    """Doc"""\n'
        '    Simu1 = import_class("Simu1")\n'
        "    return Simu1()\n"
    )
    result = _static_local_class_imports(
        source, "pyleecan", GEN_DICT, "Output", guard_comment=LOCAL_IMPORT_GUARD
    )
    assert (
        f"    # {LOCAL_IMPORT_GUARD}\n"
        "    from pyleecan.Classes_new.simu_1 import Simu1\n"
    ) in result
    assert "import_class" not in result
    # Kept local by the class generator when it reads the module again
    import ast

    node = next(n for n in ast.walk(ast.parse(result)) if isinstance(n, ast.ImportFrom))
    assert _has_method_body_import_guard(result, node)


def test_static_imports_without_guard_unchanged():
    source = LOADER + 'def f():\n    Simu1 = import_class("Simu1")\n    return Simu1\n'
    result = _static_local_class_imports(source, "pyleecan", GEN_DICT, "Output")
    assert "#" not in result


def test_static_imports_accept_legacy_normalization_names():
    source = LOADER + (
        "def f(obj):\n"
        '    Norm_ref = import_class("Norm_ref", "normalizations")\n'
        "    return Norm_ref(ref=obj)\n"
    )
    result = _static_local_class_imports(source, "pyleecan", GEN_DICT, "Data")
    assert "from pyleecan.Classes_new.norm_ref import NormRef as Norm_ref" in result
    assert "import_class" not in result


def test_drop_guarded_header_duplicates():
    guard = f"# {LOCAL_IMPORT_GUARD}"
    source = (
        "from .opti_objective import OptiObjective\n"
        "\n"
        "\n"
        "class VarOpti:\n"
        "    def check(self):\n"
        f"        {guard}\n"
        "        from .opti_objective import OptiObjective\n"
        "        from .simu_1 import Simu1\n"
        "\n"
        "        return OptiObjective, Simu1\n"
        "\n"
        "    def other(self):\n"
        f"        {guard}\n"
        "        from .opti_objective import OptiObjective\n"
        "\n"
        "        return OptiObjective\n"
        "\n"
        "    def unguarded(self):\n"
        "        from .opti_objective import OptiObjective\n"
        "\n"
        "        return OptiObjective\n"
    )
    result = _drop_guarded_header_duplicates(source)
    check = result.split("def check")[1].split("def other")[0]
    assert "from .opti_objective import OptiObjective" not in check
    assert guard in check and "from .simu_1 import Simu1" in check
    other = result.split("def other")[1].split("def unguarded")[0]
    assert guard not in other and "import" not in other  # Guard left alone: removed
    unguarded = result.split("def unguarded")[1]
    assert "from .opti_objective import OptiObjective" in unguarded  # Not guarded
    assert _drop_guarded_header_duplicates(result) == result


def test_methods_new_has_no_legacy_class_loader():
    """The generated Methods_new: no import_class of the legacy package."""
    from pathlib import Path

    from pyleecan.definitions import MAIN_DIR

    sources = [
        path.read_text(encoding="utf-8")
        for path in Path(MAIN_DIR, "Methods_new").rglob("*.py")
    ]
    assert not any('import_class("pyleecan.Classes"' in text for text in sources)
    assert not any("from ....Methods import" in text for text in sources)
    assert not any("from ....Functions.load import" in text for text in sources)
