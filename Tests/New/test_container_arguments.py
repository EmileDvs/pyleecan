"""Container arguments replacing the parent reads (PLAN.md Step 11)."""

import ast

from pyleecan.Generator.ClassGenerator.New.container_arguments import (
    add_container_arguments,
)

GEN_DICT = {
    "Slot": {"mother": "", "properties": []},
    "SlotW10": {"mother": "Slot", "properties": []},
    "Lamination": {"mother": "", "properties": [{"name": "slot", "type": "Slot"}]},
    "Machine": {"mother": "", "properties": [{"name": "stator", "type": "Lamination"}]},
}
PACKAGE = "pyleecan.Methods_new.slot.SlotW10"


def test_method_reading_its_container():
    source = (
        '"""Module"""\n'
        "def get_surface_active(self, alpha=0, delta=0):\n"
        '    """Return the surface\n\n'
        "    Parameters\n"
        "    ----------\n"
        "    alpha : float\n"
        "        rotation\n\n"
        "    Returns\n"
        "    -------\n"
        "    surf : Surface\n"
        "        Surface\n"
        '    """\n'
        "    if self.parent is None:\n"
        "        return None\n"
        '    return self.parent.get_label() + "_W"\n'
    )
    result = add_container_arguments(source, PACKAGE, "SlotW10", GEN_DICT)
    ast.parse(result)
    assert "def get_surface_active(self, alpha=0, delta=0, lam=None):\n" in result
    assert (
        "    alpha : float\n"
        "        rotation\n"
        "    lam : Lamination or Notch, optional\n"
        "        Lamination (or notch) holding the slot (default: the parent)\n\n"
        "    Returns\n"
    ) in result
    assert (
        '    """\n    lam = container_or_parent(self, lam, "lam")\n    if lam is None:\n'
        in result
    )
    assert '    return lam.get_label() + "_W"\n' in result
    assert result.startswith(
        '"""Module"""\nfrom ....classes_common.parents import container_or_parent\n'
    )
    # Idempotent
    assert add_container_arguments(result, PACKAGE, "SlotW10", GEN_DICT) == result


def test_override_and_self_calls():
    """An override without parent read gets the argument and passes it on."""
    source = (
        "def comp_height_active(self, Ndisc=200):\n"
        '    """Height"""\n'
        "    surf = self.get_surface_active()\n"
        "    return surf.comp_height(Ndisc=Ndisc) + self.comp_height()\n"
    )
    result = add_container_arguments(
        source, "pyleecan.Methods_new.slot.Slot", "Slot", GEN_DICT
    )
    assert "def comp_height_active(self, Ndisc=200, lam=None):\n" in result
    assert "    surf = self.get_surface_active(lam=lam)\n" in result
    assert "self.comp_height()" in result  # Not a listed method
    assert "container_or_parent" not in result


def test_container_calls():
    """The container passes itself; other receivers are left to the fallback."""
    source = (
        "def build_geometry(self, slot):\n"
        '    """Build"""\n'
        "    surf = self.slot.get_surface_active(alpha=1)\n"
        "    H = self.slot.comp_height_active()\n"
        "    other = slot.get_surface_active()\n"
        "    return surf, H, other\n"
    )
    package = "pyleecan.Methods_new.machine.Lamination"
    result = add_container_arguments(source, package, "Lamination", GEN_DICT)
    assert "self.slot.get_surface_active(alpha=1, lam=self)" in result
    assert "self.slot.comp_height_active(lam=self)" in result
    assert "other = slot.get_surface_active()\n" in result
    # A field of another family
    source = "def f(self):\n    return self.stator.get_surface_active()\n"
    assert (
        add_container_arguments(source, "x.y.z.Machine", "Machine", GEN_DICT) == source
    )
