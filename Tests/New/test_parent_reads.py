"""Classification of the parent reads of Methods_new (PLAN.md Step 11)."""

import ast

from pyleecan.Generator.ClassGenerator.New.parent_reads import (
    classify_function,
    classify_methods_new,
)


def _function(source):
    return ast.parse(source).body[0]


def test_classify_function():
    source = (
        "def comp(self):\n"
        "    if self.parent is None:\n"
        "        return None\n"
        "    label = self.parent.get_label()\n"
        "    Rbo = self.parent.get_Rbo()\n"
        "    output = self.parent.parent.parent\n"
        "    return f(self.parent, Rbo, label, output)\n"
    )
    patterns = classify_function(_function(source))
    assert patterns == {"check": 1, "label": 1, "container": 1, "walk": 1, "other": 1}
    assert not classify_function(_function("def f(self, x):\n    return x.parent\n"))


def test_mechanical(tmp_path):
    """A method called only on a typed field of its container is mechanical."""
    files = {
        "slot/Slot/comp_height.py": "def comp_height(self):\n    return self.parent.Rint\n",
        "slot/Slot/comp_area.py": "def comp_area(self):\n    return self.comp_height()\n",
        "slot/Slot/get_Rbo.py": "def get_Rbo(self):\n    return self.parent.get_Rbo()\n",
        "machine/Lamination/comp.py": "def comp(self):\n    return self.slot.comp_height()\n",
        "machine/Machine/comp.py": "def comp(self, lam):\n    return lam.get_Rbo()\n",
    }
    for name, source in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    gen_dict = {
        "Slot": {"mother": "", "properties": []},
        "Lamination": {"mother": "", "properties": [{"name": "slot", "type": "Slot"}]},
        "Machine": {"mother": "", "properties": []},
    }
    methods = classify_methods_new(tmp_path, gen_dict)
    assert set(methods) == {("Slot", "comp_height"), ("Slot", "get_Rbo")}
    assert methods["Slot", "comp_height"]["mechanical"]
    assert not methods["Slot", "get_Rbo"][
        "mechanical"
    ]  # lam.get_Rbo(): unknown receiver
