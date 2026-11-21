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


def _is_self_parent(node):
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "parent"
        and isinstance(node.ctx, ast.Load)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    )


def _docstring_entry(lines, function, spec):
    """(line index, lines) adding the argument to the docstring, or None."""
    if ast.get_docstring(function) is None:
        return None
    doc = function.body[0]
    start, end = doc.lineno - 1, doc.end_lineno  # Lines of the docstring
    if end - start < 2:
        return None  # One-line docstring
    indent = " " * function.body[0].col_offset
    entry = [
        f"{indent}{spec.name} : {spec.doc_type}, optional\n",
        f"{indent}    {spec.description}\n",
    ]

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
        return last, entry
    # No Parameters section: before the first section, else before the end
    stop = sections[0] if sections else end - 1
    block = [f"{indent}Parameters\n", f"{indent}----------\n", *entry, "\n"]
    if not sections:
        block = ["\n", *block[:-1]]
    return stop, block


def add_container_arguments(source, package, class_name, gen_dict):
    """Add the container arguments of CONTAINER_ARGUMENTS to a method module.

    - a method of the list in a class of the family gets the argument (and
      its docstring entry); when it reads ``self.parent``, the container is
      read once with ``container_or_parent`` and ``self.parent`` replaced;
      its calls of the listed methods on ``self`` pass the argument on;
    - in the methods of any class, the calls of the listed methods on a field
      typed in the family (``self.slot.get_surface_active()``) pass ``self``.

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
    insertions = []  # (position, text) in the source
    line_insertions = []  # (line index, lines)
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
        argument_names = {
            a.arg for a in [*function.args.args, *function.args.kwonlyargs]
        }
        if own is not None and own.name not in argument_names:
            # The argument, after the last one (before **kwargs)
            args = function.args
            nodes = [*args.args, *args.defaults, *args.kwonlyargs]
            nodes += [d for d in args.kw_defaults if d is not None]
            if args.vararg is not None:
                nodes.append(args.vararg)
            last = max(nodes, key=lambda n: (n.end_lineno, n.end_col_offset))
            text = f", {own.name}=None"
            insertions.append(
                (_position(offsets, last.end_lineno, last.end_col_offset), text)
            )
            entry = _docstring_entry(lines, function, own)
            if entry is not None:
                line_insertions.append(entry)
            reads = [node for node in ast.walk(function) if _is_self_parent(node)]
            if reads:
                fallback = True
                for node in reads:
                    start = _position(offsets, node.lineno, node.col_offset)
                    end = _position(offsets, node.end_lineno, node.end_col_offset)
                    insertions.append((start, None, end, own.name))
                # The container read once, after the docstring
                body = function.body[0]
                indent = " " * body.col_offset
                depth = f", depth={own.depth}" if own.depth != 1 else ""
                line = f'{indent}{own.name} = container_or_parent(self, {own.name}, "{own.name}"{depth})\n'
                if ast.get_docstring(function) is not None:
                    line_insertions.append((body.end_lineno, [line]))
                else:
                    line_insertions.append((body.lineno - 1, [line]))
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            ):
                continue
            receiver = node.func.value
            for spec in CONTAINER_ARGUMENTS:
                if node.func.attr not in spec.methods or _has_keyword(node, spec.name):
                    continue
                if (
                    isinstance(receiver, ast.Name)
                    and receiver.id == "self"
                    and own is spec
                ):
                    insertions.append(
                        _keyword_insertion(
                            source, offsets, node, f"{spec.name}={spec.name}"
                        )
                    )
                elif (
                    isinstance(receiver, ast.Attribute)
                    and isinstance(receiver.value, ast.Name)
                    and receiver.value.id == "self"
                    and fields.get(receiver.attr) in families[spec.base]
                ):
                    insertions.append(
                        _keyword_insertion(source, offsets, node, f"{spec.name}=self")
                    )
    if not insertions and not line_insertions:
        return source
    # Text edits from the end (positions of the original source)
    for edit in sorted(insertions, key=lambda e: e[0], reverse=True):
        if len(edit) == 2:
            position, text = edit
            source = source[:position] + text + source[position:]
        else:
            start, _, end, text = edit
            source = source[:start] + text + source[end:]
    # Line insertions: the text edits above do not add lines before them
    # (one-line edits), so the line indexes still hold
    lines = source.splitlines(keepends=True)
    for index, new_lines in sorted(line_insertions, key=lambda e: e[0], reverse=True):
        lines[index:index] = new_lines
    source = "".join(lines)
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
