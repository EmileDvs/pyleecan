"""Container arguments replacing the parent reads (PLAN.md Step 11).

A method reading its container through the legacy parent link
(``self.parent.get_label()`` in a slot) gets the container as an optional
argument, with the parent as fallback::

    def get_surface_active(self, alpha=0, delta=0, lam=None):
        lam = container_or_parent(self, lam, "lam")
        label = lam.get_label() + ...

and the generator makes the calls of the container pass it
(``self.slot.get_surface_active(lam=self)`` in a ``Lamination`` method). The
argument is added to every override of the method in the class family, so that
any member accepts it. Other calls (the tests, user scripts) keep working
through the fallback (``classes_common.parents.container_or_parent``), which
Phase 2 deprecates.

Only the "mechanical" methods are listed here: their call sites in Methods_new
all know the container (``parent_reads.py``).
"""

import ast
import re
from typing import NamedTuple

FALLBACK_MODULE = "classes_common.parents"
"""Module of container_or_parent below pyleecan"""


class ContainerArgument(NamedTuple):
    """Methods of a class family taking their container as an argument."""

    base: str
    """Root class of the family (its descendants included)"""
    methods: tuple
    """Method names"""
    name: str
    """Name of the argument"""
    doc_type: str
    """Documented type (numpydoc, turned into the hint by type_hints.py)"""
    description: str
    """Documentation of the argument"""
    depth: int = 1
    """Number of parent links up to the container"""
    caller_value: str = "self"
    """Value passed by the calls on a field of the container: ``self`` (the
    container), or a local name of the calling method (``output``)"""
    callers: tuple = ()
    """(class, method, value): calls of the listed methods on ``self`` in that
    method pass value (e.g. ``Simulation.run`` passes its ``results``)"""


CONTAINER_ARGUMENTS = (
    ContainerArgument(
        base="Slot",
        methods=(
            "comp_height_active",
            "get_surface_active",
            "get_surface_opening",
            "get_surface_wedges",
        ),
        name="lam",
        doc_type="Lamination or Notch",
        description="Lamination (or notch) holding the slot (default: the parent)",
    ),
    # The models of a simulation: run(output), called by Simu1.run_single
    *(
        ContainerArgument(
            base=model,
            methods=("run",),
            name="output",
            doc_type="Output",
            description="Output of the simulation (default: the parent of the simulation)",
            depth=2,
            caller_value="output",
        )
        for model in ("Electrical", "Magnetics", "Force", "Structural", "Loss")
    ),
    # The simulation run in its output (pass 3): Simulation.run passes the
    # output it creates or receives
    ContainerArgument(
        base="Simulation",
        methods=("run_single",),
        name="output",
        doc_type="Output",
        description="Output of the simulation (default: the parent)",
        callers=(("Simulation", "run", "results"),),
    ),
)
"""Container arguments added by the generator (Step 11 passes)"""


def _lineage(gen_dict, name):
    names = []
    while name and name in gen_dict and name not in names:
        names.append(name)
        name = gen_dict[name].get("mother") or None
    return names


def family(gen_dict, base):
    """base and the classes inheriting from it."""
    return frozenset(cls for cls in gen_dict if base in _lineage(gen_dict, cls))


def _field_types(gen_dict, class_name):
    """{field: class name} of a class and its mothers."""
    fields = {}
    for name in _lineage(gen_dict, class_name):
        for prop in gen_dict[name].get("properties", []):
            prop_type = str(prop.get("type", "")).split(".")[-1]
            fields.setdefault(prop["name"], prop_type)
    return fields


def fallback_methods(gen_dict, methods_dir):
    """(class, method, argument) of the methods given a container argument.

    Parameters
    ----------
    gen_dict : dict
        Generation dictionary
    methods_dir : Path
        Methods_new folder

    Returns
    -------
    methods : list
        Sorted (class name, method name, argument name)
    """
    from pathlib import Path

    from .class_generator import class_subpackage

    found = []
    for spec in CONTAINER_ARGUMENTS:
        for class_name in family(gen_dict, spec.base):
            folder = (
                Path(methods_dir) / class_subpackage(class_name, gen_dict) / class_name
            )
            for method in spec.methods:
                if (folder / f"{method}.py").is_file():
                    found.append((class_name, method, spec.name))
    return sorted(found)


def _offsets(source):
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _position(offsets, line, col):
    return offsets[line - 1] + col


def _keyword_insertion(source, offsets, call, text):
    """(position, text) adding a keyword argument to a call."""
    nodes = [*call.args, *call.keywords]
    if nodes:
        last = max(nodes, key=lambda n: (n.end_lineno, n.end_col_offset))
        return _position(offsets, last.end_lineno, last.end_col_offset), ", " + text
    # No argument: after the opening parenthesis
    start = _position(offsets, call.func.end_lineno, call.func.end_col_offset)
    return source.index("(", start) + 1, text


def _has_keyword(call, name):
    return any(keyword.arg == name for keyword in call.keywords) or any(
        keyword.arg is None for keyword in call.keywords
    )


def _parent_chain(node):
    """Number of ``.parent`` of a ``self.parent.parent...`` read (0 otherwise)."""
    length = 0
    while (
        isinstance(node, ast.Attribute)
        and node.attr == "parent"
        and isinstance(node.ctx, ast.Load)
    ):
        length += 1
        node = node.value
    return length if isinstance(node, ast.Name) and node.id == "self" else 0


def _is_none_test(node):
    """``x is None`` (one comparison)."""
    return (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Is)
        and isinstance(node.comparators[0], ast.Constant)
        and node.comparators[0].value is None
    )


DROPPED = "# <container_or_parent: dropped>\n"
"""Marker of a line removed by the pass (the container assignment)"""

ONE_LINE_DOCSTRING = re.compile(r"^(\s*)(\"\"\"|''')(.*)\2\s*$")


def _docstring_entry(lines, function, spec):
    """(line index, deleted lines, new lines) documenting the argument, or None."""
    if ast.get_docstring(function) is None:
        return None
    doc = function.body[0]
    start, end = doc.lineno - 1, doc.end_lineno  # Lines of the docstring
    indent = " " * doc.col_offset
    entry = [
        f"{indent}{spec.name} : {spec.doc_type}, optional\n",
        f"{indent}    {spec.description}\n",
    ]
    if end - start < 2:  # One-line docstring: made a multi-line one
        found = ONE_LINE_DOCSTRING.match(lines[start])
        if found is None:
            return None
        quotes = found.group(2)
        return (
            start,
            1,
            [
                f"{indent}{quotes}{found.group(3)}\n",
                "\n",
                f"{indent}Parameters\n",
                f"{indent}----------\n",
                *entry,
                f"{indent}{quotes}\n",
            ],
        )

    def header(index):
        return (
            index + 1 < end
            and lines[index].strip()
            and set(lines[index + 1].strip()) == {"-"}
        )

    sections = [index for index in range(start, end) if header(index)]
    parameters = [index for index in sections if lines[index].strip() == "Parameters"]
    if parameters:
        index = parameters[0] + 2
        following = [section for section in sections if section > parameters[0]]
        stop = following[0] if following else end - 1
        last = index
        for line_index in range(index, stop):
            if lines[line_index].strip():
                last = line_index + 1
        return last, 0, entry
    # No Parameters section: before the first section, else before the end
    stop = sections[0] if sections else end - 1
    block = [f"{indent}Parameters\n", f"{indent}----------\n", *entry, "\n"]
    if not sections:
        block = ["\n", *block[:-1]]
    return stop, 0, block


def _local_names(function):
    """Arguments and assigned names of a function."""
    args = function.args
    names = {a.arg for a in [*args.posonlyargs, *args.args, *args.kwonlyargs]}
    names |= {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    return names


def _own_method_edits(source, offsets, lines, function, spec):
    """Text and line edits of a method given the container argument."""
    text_edits = []  # (start, end, text)
    line_edits = []  # (line index, deleted lines, new lines)
    args = function.args
    # The argument, after the last one (before **kwargs)
    nodes = [*args.posonlyargs, *args.args, *args.defaults, *args.kwonlyargs]
    nodes += [d for d in args.kw_defaults if d is not None]
    if args.vararg is not None:
        nodes.append(args.vararg)
    last = max(nodes, key=lambda n: (n.end_lineno, n.end_col_offset))
    position = _position(offsets, last.end_lineno, last.end_col_offset)
    text_edits.append((position, position, f", {spec.name}=None"))
    entry = _docstring_entry(lines, function, spec)
    if entry is not None:
        line_edits.append(entry)
    parents = {}
    for node in ast.walk(function):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    reads = []  # Reads of the container: self.parent * depth
    tests = []  # None tests of a shorter chain (depth > 1)
    dropped = []  # Statements "name = self.parent * depth"
    for node in ast.walk(function):
        if isinstance(node, ast.Assign) and (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == spec.name
            and _parent_chain(node.value) == spec.depth
        ):
            dropped.append(node)
        length = _parent_chain(node)
        if length == 0:
            continue
        outer = parents.get(id(node))
        if length == spec.depth:
            reads.append(node)
        elif length < spec.depth and _parent_chain(outer) == 0 and _is_none_test(outer):
            tests.append(outer)
    if not reads:
        return text_edits, line_edits, False
    dropped_values = {id(node.value) for node in dropped}
    for node in reads:
        if id(node) in dropped_values:
            continue
        start = _position(offsets, node.lineno, node.col_offset)
        end = _position(offsets, node.end_lineno, node.end_col_offset)
        text_edits.append((start, end, spec.name))
    for node in tests:
        # The parent links are checked only without the container
        start = _position(offsets, node.lineno, node.col_offset)
        end = _position(offsets, node.end_lineno, node.end_col_offset)
        text = f"{spec.name} is None and {source[start:end]}"
        if not isinstance(parents.get(id(node)), (ast.If, ast.While)):
            text = f"({text})"
        text_edits.append((start, end, text))
    for node in dropped:
        indent = " " * node.col_offset
        line_edits.append(
            (node.lineno - 1, node.end_lineno - node.lineno + 1, [indent + DROPPED])
        )
    # The container read once, after the docstring
    body = function.body[0]
    indent = " " * body.col_offset
    depth = f", depth={spec.depth}" if spec.depth != 1 else ""
    line = (
        f"{indent}{spec.name} = container_or_parent("
        f'self, {spec.name}, "{spec.name}"{depth})\n'
    )
    if ast.get_docstring(function) is not None:
        line_edits.append((body.end_lineno, 0, [line]))
    else:
        line_edits.append((body.lineno - 1, 0, [line]))
    return text_edits, line_edits, True


def add_container_arguments(source, package, class_name, gen_dict):
    """Add the container arguments of CONTAINER_ARGUMENTS to a method module.

    - a method of the list in a class of the family gets the argument (and
      its docstring entry); when it reads the container (``self.parent``, or
      ``self.parent.parent`` for a depth of 2), the container is read once
      with ``container_or_parent`` and the reads replaced (the shorter chains
      tested against None are tested only without the container); its calls
      of the listed methods on ``self`` pass the argument on;
    - in the methods of any class, the calls of the listed methods on a field
      typed in the family (``self.slot.get_surface_active()``) pass the
      container (``caller_value``: ``self``, or a local name of the caller).

    Parameters
    ----------
    source : str
        Source of a method module
    package : str
        Package of the module (relative import of classes_common)
    class_name : str or None
        Class of the method module
    gen_dict : dict
        Generation dictionary

    Returns
    -------
    source : str
        Source with the container arguments
    """
    if class_name is None or class_name not in gen_dict:
        return source
    if not any(
        method in source for spec in CONTAINER_ARGUMENTS for method in spec.methods
    ):
        return source
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = _offsets(source)
    text_edits = []  # (start, end, text) in the source
    line_edits = []  # (line index, deleted lines, new lines)
    fields = _field_types(gen_dict, class_name)
    families = {spec.base: family(gen_dict, spec.base) for spec in CONTAINER_ARGUMENTS}
    fallback = False
    for function in tree.body:
        if not isinstance(function, ast.FunctionDef):
            continue
        own = next(
            (
                spec
                for spec in CONTAINER_ARGUMENTS
                if function.name in spec.methods and class_name in families[spec.base]
            ),
            None,
        )
        local_names = _local_names(function)
        if own is not None and own.name not in {
            a.arg for a in [*function.args.args, *function.args.kwonlyargs]
        }:
            texts, line_changes, reads = _own_method_edits(
                source, offsets, lines, function, own
            )
            text_edits += texts
            line_edits += line_changes
            fallback |= reads
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            ):
                continue
            receiver = node.func.value
            for spec in CONTAINER_ARGUMENTS:
                if node.func.attr not in spec.methods or _has_keyword(node, spec.name):
                    continue
                if isinstance(receiver, ast.Name) and receiver.id == "self":
                    value = next(
                        (
                            value
                            for caller_class, caller_method, value in spec.callers
                            if caller_class == class_name
                            and caller_method == function.name
                        ),
                        spec.name if own is spec else None,
                    )
                    if value is not None:
                        position, text = _keyword_insertion(
                            source, offsets, node, f"{spec.name}={value}"
                        )
                        text_edits.append((position, position, text))
                elif (
                    isinstance(receiver, ast.Attribute)
                    and isinstance(receiver.value, ast.Name)
                    and receiver.value.id == "self"
                    and fields.get(receiver.attr) in families[spec.base]
                    and (
                        spec.caller_value == "self" or spec.caller_value in local_names
                    )
                ):
                    position, text = _keyword_insertion(
                        source, offsets, node, f"{spec.name}={spec.caller_value}"
                    )
                    text_edits.append((position, position, text))
    if not text_edits and not line_edits:
        return source
    # Text edits from the end (positions of the original source); they do
    # not add or remove lines, so the line indexes of line_edits still hold
    for start, end, text in sorted(text_edits, key=lambda e: e[:2], reverse=True):
        source = source[:start] + text + source[end:]
    lines = source.splitlines(keepends=True)
    for index, deleted, new_lines in sorted(
        line_edits, key=lambda e: e[0], reverse=True
    ):
        lines[index : index + deleted] = new_lines
    # Dropped statements removed, with the blank line after them when the line
    # before is blank
    kept = []
    skip_blank = False
    for line in lines:
        if line.strip() == DROPPED.strip():
            skip_blank = bool(kept) and not kept[-1].strip()
            continue
        if skip_blank and not line.strip():
            skip_blank = False
            continue
        skip_blank = False
        kept.append(line)
    source = "".join(kept)
    if fallback and "import container_or_parent" not in source:
        up = "." * len(package.split("."))
        from .modernize import _module_import_position

        lines = source.splitlines(keepends=True)
        lines.insert(
            _module_import_position(ast.parse(source)),
            f"from {up}{FALLBACK_MODULE} import container_or_parent\n",
        )
        source = "".join(lines)
    return source
