import ast
import os
import shutil
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pyleecan.Classes_new.arc_1 import Arc1
from pyleecan.Classes_new.arc_2 import Arc2
from pyleecan.Classes_new.arc_3 import Arc3
from pyleecan.Classes_new.segment import Segment
from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _keyword_geometry_calls,
    generate_class,
)
from pyleecan.Generator.read_fct import read_all


def test_segment_calls_preserve_expressions_comments_and_aliases():
    source = """\
from pyleecan.Classes_new.segment import Segment as Edge
from other import Segment
def draw():
    return Edge(
        (1 + 2),  # begin
        Edge(3, 4).end,
        {"name": "segment"},
    )
"""
    result = _keyword_geometry_calls(source, "pyleecan")
    assert "begin=(1 + 2),  # begin" in result
    assert "end=Edge(begin=3, end=4).end" in result
    assert 'prop_dict={"name": "segment"}' in result
    namespace = {"__name__": "pyleecan.Classes_new.example"}
    # Execute only the function; the other import deliberately is not rewritten.
    code = ast.parse(result)
    code.body = [node for node in code.body if isinstance(node, ast.FunctionDef)]
    namespace["Edge"] = Segment
    exec(compile(code, "<test>", "exec"), namespace)
    segment = namespace["draw"]()
    assert (segment.begin, segment.end, segment.prop_dict) == (
        3,
        4,
        {"name": "segment"},
    )


@pytest.mark.parametrize(
    "source",
    [
        "from pyleecan.Classes_new.segment import Segment\nSegment(*args)\n",
        "from pyleecan.Classes_new.segment import Segment\nSegment(1, begin=2)\n",
        "from pyleecan.Classes_new.segment import Segment\ndef f(Segment):\n    return Segment(1)\n",
        "from pyleecan.Classes_new.segment import Segment\nfrom other import Segment\nSegment(1)\n",
    ],
)
def test_unsafe_segment_calls_are_rejected(source):
    with pytest.raises(ValueError, match="Segment|geometry"):
        _keyword_geometry_calls(source, "pyleecan")


def test_unrelated_calls_remain_unchanged():
    source = "from other import Segment\nvalue = Segment(1, 2)\n"
    assert _keyword_geometry_calls(source, "pyleecan") == source


@pytest.mark.parametrize(
    ("name", "module", "cls", "args", "expected"),
    [
        ("Arc1", "arc_1", Arc1, "1, 2, 3, False, {'id': 4}", (1, 2, 3, False)),
        ("Arc2", "arc_2", Arc2, "1, 2, 3, {'id': 4}", (1, 2, 3)),
        ("Arc3", "arc_3", Arc3, "1, 2, False, {'id': 4}", (1, 2, False)),
    ],
)
def test_arc_legacy_positional_arguments(name, module, cls, args, expected):
    source = f"from .{module} import {name} as Curve\nresult = Curve({args})\n"
    result = _keyword_geometry_calls(source, "pyleecan")
    tree = ast.parse(result)
    call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call))
    assert not call.args
    assert [keyword.arg for keyword in call.keywords] == {
        "Arc1": ["begin", "end", "radius", "is_trigo_direction", "prop_dict"],
        "Arc2": ["begin", "center", "angle", "prop_dict"],
        "Arc3": ["begin", "end", "is_trigo_direction", "prop_dict"],
    }[name]
    tree.body = [node for node in tree.body if not isinstance(node, ast.ImportFrom)]
    namespace = {"Curve": cls}
    exec(compile(tree, "<test>", "exec"), namespace)
    arc = namespace["result"]
    fields = {
        "Arc1": ("begin", "end", "radius", "is_trigo_direction"),
        "Arc2": ("begin", "center", "angle"),
        "Arc3": ("begin", "end", "is_trigo_direction"),
    }[name]
    assert tuple(getattr(arc, field) for field in fields) == expected
    assert arc.prop_dict == {"id": 4}


@pytest.mark.parametrize(
    "name,module", [("Arc1", "arc_1"), ("Arc2", "arc_2"), ("Arc3", "arc_3")]
)
def test_arc_unsafe_calls_are_rejected(name, module):
    prefix = f"from pyleecan.Classes_new.{module} import {name}\n"
    for call in (f"{name}(*args)", f"{name}(1, begin=2)"):
        with pytest.raises(ValueError, match=name):
            _keyword_geometry_calls(prefix + call + "\n", "pyleecan")


def test_geometry_import_collision_is_rejected():
    source = (
        "from .arc_1 import Arc1 as Curve\nfrom .arc_2 import Arc2 as Curve\nCurve(1)\n"
    )
    with pytest.raises(ValueError, match="conflicting"):
        _keyword_geometry_calls(source, "pyleecan")


@pytest.mark.parametrize(
    ("name", "category", "method", "expected"),
    [
        ("Circle", "Geometry", "get_lines", {"Arc3": 2}),
        ("Frame", "Machine", "build_geometry", {"Arc1": 2, "Segment": 2}),
        (
            "FrameBar",
            "Machine",
            "build_geometry_bar",
            {"Arc1": 1, "Arc2": 1, "Segment": 2},
        ),
    ],
)
def test_generator_rewrites_arc_calls(
    tmp_path, monkeypatch, name, category, method, expected
):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    methods = tmp_path / "Methods" / category / name
    methods.mkdir(parents=True)
    shutil.copyfile(
        Path(MAIN_DIR) / "Methods" / category / name / (method + ".py"),
        methods / (method + ".py"),
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict[name] = deepcopy(gen_dict[name])
    gen_dict[name]["methods"] = [method]
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = generate_class(gen_dict, name, str(output))
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for symbol, count in expected.items():
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == symbol
        ]
        assert len(calls) == count
        assert all(not call.args for call in calls)
        assert all(call.keywords[0].arg == "begin" for call in calls)


def test_generator_preserves_lamination_segment_arguments(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    methods = tmp_path / "Methods" / "Machine" / "Lamination"
    methods.mkdir(parents=True)
    shutil.copyfile(
        Path(MAIN_DIR)
        / "Methods"
        / "Machine"
        / "Lamination"
        / "build_yoke_side_line.py",
        methods / "build_yoke_side_line.py",
    )
    gen_dict = read_all(DOC_DIR)
    gen_dict["Lamination"] = deepcopy(gen_dict["Lamination"])
    gen_dict["Lamination"]["methods"] = ["build_yoke_side_line"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = generate_class(gen_dict, "Lamination", str(output))
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Segment"
    ]
    assert len(calls) == 2
    assert all(not call.args for call in calls)
    assert all(
        [kw.arg for kw in call.keywords] == ["begin", "end", "prop_dict"]
        for call in calls
    )

    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    merge = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == "merge_line_list"
    )
    merge.decorator_list = []
    namespace = {"Segment": Segment, "BOUNDARY_PROP_LAB": "boundary"}
    module = ast.fix_missing_locations(ast.Module(body=[merge], type_ignores=[]))
    exec(compile(module, "<generated>", "exec"), namespace)
    result = namespace["merge_line_list"](1, 2, "side", [])
    assert (result[0].begin, result[0].end) == (1, 2)
    assert result[0].prop_dict == {"boundary": "side-0"}
