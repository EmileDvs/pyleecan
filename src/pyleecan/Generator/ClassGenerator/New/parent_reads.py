"""Classification of the parent reads of Methods_new (PLAN.md Step 11).

Each read of ``self.parent`` in a method of ``Methods_new`` gets a pattern:

- ``logger``: ``self.parent.get_logger()`` (Step 9 removed these calls);
- ``label``: ``self.parent.get_label()`` (pattern 3: the caller passes the label);
- ``walk``: ``self.parent.parent...`` (pattern 2: a model walks up to the
  simulation and the output);
- ``check``: ``self.parent is None`` / ``is not None`` tests only;
- ``container``: ``self.parent.<attr>`` or ``self.parent.<method>()`` (pattern 1:
  a child reads its container's data);
- ``other``: the parent passed on (argument, assignment, return).

A method is **mechanical** when all its call sites in Methods_new call it on a
field of the container class from a method of that class
(``self.slot.comp_height()`` in a ``Lamination`` method): the generator can
pass ``self`` as the container. Run: ``python -m
pyleecan.Generator.ClassGenerator.New.parent_reads``.
"""

import ast
from collections import Counter, defaultdict
from pathlib import Path

PATTERNS = ("logger", "label", "walk", "check", "container", "other")


def _parent_chain_length(node):
    """Number of ``.parent`` in ``self.parent.parent...`` (0 if not a chain)."""
    length = 0
    while isinstance(node, ast.Attribute) and node.attr == "parent":
        length += 1
        node = node.value
    return length if isinstance(node, ast.Name) and node.id == "self" else 0


def classify_function(function):
    """Patterns of the parent reads of a method (Counter)."""
    patterns = Counter()
    parents = {}  # id of the outermost self.parent[.parent] nodes: parent node
    for node in ast.walk(function):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    for node in ast.walk(function):
        if not (isinstance(node, ast.Attribute) and node.attr == "parent"):
            continue
        if _parent_chain_length(node) == 0:
            continue
        outer = parents.get(id(node))
        if isinstance(outer, ast.Attribute) and outer.attr == "parent":
            continue  # Counted with the outer chain
        if _parent_chain_length(node) > 1:
            patterns["walk"] += 1
        elif isinstance(outer, ast.Attribute):
            if outer.attr == "get_logger":
                patterns["logger"] += 1
            elif outer.attr == "get_label":
                patterns["label"] += 1
            else:
                patterns["container"] += 1
        elif isinstance(outer, ast.Compare) and all(
            isinstance(op, (ast.Is, ast.IsNot)) for op in outer.ops
        ):
            patterns["check"] += 1
        else:
            patterns["other"] += 1
    return patterns


def _field_types(gen_dict):
    """{class: {field: type}} of the generation dictionary (types without [] {})."""
    types = {}
    for name, class_dict in gen_dict.items():
        fields = {}
        for prop in class_dict.get("properties", []):
            prop_type = str(prop.get("type", "")).strip("[]{}")
            fields[prop["name"]] = prop_type.split(".")[-1]
        types[name] = fields
    return types


def _lineage(gen_dict, name):
    names = []
    while name and name in gen_dict and name not in names:
        names.append(name)
        name = gen_dict[name].get("mother") or None
    return names


def classify_methods_new(methods_dir, gen_dict):
    """Parent reads of each method of Methods_new.

    Returns
    -------
    methods : dict
        {(class, method): {"package": sub-package, "patterns": Counter,
        "container_calls": calls on a typed field of the container,
        "self_calls": calls on self in the class family,
        "calls": calls on an unknown receiver, "mechanical": bool}}
    """
    methods_dir = Path(methods_dir)
    sources = {}
    for path in sorted(methods_dir.glob("*/*/*.py")):
        if path.name == "__init__.py":
            continue
        sources[path] = ast.parse(path.read_text(encoding="utf-8"))
    methods = {}
    for path, tree in sources.items():
        package, class_name = path.parts[-3], path.parts[-2]
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == path.stem:
                patterns = classify_function(node)
                if patterns:
                    methods[(class_name, node.name)] = {
                        "package": package,
                        "patterns": patterns,
                        "calls": 0,
                        "container_calls": 0,
                        "self_calls": 0,
                    }
    # Call sites: x.method(...) in the methods of the other classes
    field_types = _field_types(gen_dict)
    by_name = defaultdict(list)
    for key in methods:
        by_name[key[1]].append(key)
    for path, tree in sources.items():
        caller_class = path.parts[-2]
        caller_fields = {}
        for name in _lineage(gen_dict, caller_class):
            for field, field_type in field_types.get(name, {}).items():
                caller_fields.setdefault(field, field_type)
        caller_family = set(_lineage(gen_dict, caller_class)) | _descendants(
            gen_dict, caller_class
        )
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            ):
                continue
            value = node.func.value
            for key in by_name.get(node.func.attr, ()):
                if isinstance(value, ast.Name) and value.id == "self":
                    if key[0] in caller_family:
                        methods[key]["self_calls"] += (
                            1  # Same requirement as the caller
                        )
                    continue
                if (
                    isinstance(value, ast.Attribute)
                    and isinstance(value.value, ast.Name)
                    and value.value.id == "self"
                    and value.attr in caller_fields
                ):
                    family = _descendants(gen_dict, caller_fields[value.attr])
                    if key[0] in family:
                        methods[key]["container_calls"] += 1
                    continue  # A field of another class: not a call of this method
                methods[key]["calls"] += 1  # Unknown receiver
    for info in methods.values():
        info["mechanical"] = info["container_calls"] > 0 and info["calls"] == 0
    return methods


def _descendants(gen_dict, name):
    """name and the classes inheriting from it."""
    return {cls for cls in gen_dict if name in _lineage(gen_dict, cls)}


def report(methods):
    """Markdown table: reads per package and pattern, mechanical methods."""
    packages = defaultdict(Counter)
    mechanical = Counter()
    method_count = Counter()
    for info in methods.values():
        packages[info["package"]].update(info["patterns"])
        method_count[info["package"]] += 1
        mechanical[info["package"]] += info["mechanical"]
    lines = [
        "| Package | Methods | " + " | ".join(PATTERNS) + " | Mechanical methods |",
        "|---|---" + "|---" * len(PATTERNS) + "|---|",
    ]
    for package in sorted(packages):
        counts = packages[package]
        lines.append(
            f"| {package} | {method_count[package]} | "
            + " | ".join(str(counts.get(p, 0)) for p in PATTERNS)
            + f" | {mechanical[package]} |"
        )
    total = Counter()
    for counts in packages.values():
        total.update(counts)
    lines.append(
        f"| **total** | {sum(method_count.values())} | "
        + " | ".join(str(total.get(p, 0)) for p in PATTERNS)
        + f" | {sum(mechanical.values())} |"
    )
    return "\n".join(lines)


def main():
    from pyleecan.definitions import MAIN_DIR

    from .source_names import name_maps

    methods = classify_methods_new(Path(MAIN_DIR) / "Methods_new", name_maps().gen_dict)
    print(report(methods))


if __name__ == "__main__":
    main()
