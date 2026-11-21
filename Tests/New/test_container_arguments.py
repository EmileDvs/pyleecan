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


MODEL_GEN_DICT = {
    "Electrical": {"mother": "", "properties": []},
    "Simulation": {"mother": "", "properties": []},
    "Simu1": {
        "mother": "Simulation",
        "properties": [{"name": "elec", "type": "Electrical"}],
    },
}


def test_model_run_depth_2():
    """run(output): the guards check the parent links only without output."""
    source = (
        "def run(self):\n"
        '    """Run the Electrical module"""\n'
        "    if self.parent is None:\n"
        '        raise InputError("in a Simulation")\n'
        "    if self.parent.parent is None:\n"
        '        raise InputError("in an Output")\n\n'
        "    output = self.parent.parent\n\n"
        "    machine = output.simu.machine\n"
    )
    package = "pyleecan.Methods_new.electrical.Electrical"
    result = add_container_arguments(source, package, "Electrical", MODEL_GEN_DICT)
    ast.parse(result)
    assert result == (
        "from ....classes_common.parents import container_or_parent\n"
        "def run(self, output=None):\n"
        '    """Run the Electrical module\n\n'
        "    Parameters\n"
        "    ----------\n"
        "    output : Output, optional\n"
        "        Output of the simulation (default: the parent of the simulation)\n"
        '    """\n'
        '    output = container_or_parent(self, output, "output", depth=2)\n'
        "    if output is None and self.parent is None:\n"
        '        raise InputError("in a Simulation")\n'
        "    if output is None:\n"
        '        raise InputError("in an Output")\n\n'
        "    machine = output.simu.machine\n"
    )
    assert (
        add_container_arguments(result, package, "Electrical", MODEL_GEN_DICT) == result
    )


def test_model_run_caller():
    """The simulation passes its output (a local name of the caller)."""
    source = (
        "def run_single(self):\n"
        "    output = self.parent\n"
        "    if self.elec is not None:\n"
        "        self.elec.run()\n"
    )
    package = "pyleecan.Methods_new.simulation.Simu1"
    result = add_container_arguments(source, package, "Simu1", MODEL_GEN_DICT)
    assert "        self.elec.run(output=output)\n" in result
    # Without the local name: left to the fallback
    source = "def f(self):\n    self.elec.run()\n"
    assert add_container_arguments(source, package, "Simu1", MODEL_GEN_DICT) == source


def test_explicit_caller():
    """Simulation.run passes its local results to self.run_single (pass 3)."""
    gen_dict = {
        "Simulation": {"mother": "", "properties": []},
        "Simu1": {"mother": "Simulation", "properties": []},
    }
    source = (
        "def run(self):\n"
        '    """Run"""\n'
        "    results = self.parent\n"
        "    self.run_single()\n"
        "    return results\n"
    )
    result = add_container_arguments(
        source, "pyleecan.Methods_new.simulation.Simulation", "Simulation", gen_dict
    )
    assert "    self.run_single(output=results)\n" in result
    source = (
        "def run_single(self):\n"
        '    """Run the simulation"""\n'
        "    if self.parent is None:\n"
        '        raise InputError("in an Output")\n'
        "    output = self.parent\n"
        "    output.geo = 1\n"
    )
    result = add_container_arguments(
        source, "pyleecan.Methods_new.simulation.Simu1", "Simu1", gen_dict
    )
    assert "def run_single(self, output=None):\n" in result
    assert '    output = container_or_parent(self, output, "output")\n' in result
    assert "    if output is None:\n" in result
    assert "    output = self.parent\n" not in result


LOSS_GEN_DICT = {
    "LossModel": {"mother": "", "properties": []},
    "LossModelJoule": {"mother": "LossModel", "properties": []},
    "Loss": {"mother": "", "properties": [{"name": "model_dict", "type": "{LossModel}"}]},
}


def test_two_containers():
    """A loss model reads its Loss (depth 1) and the output (depth 3)."""
    source = (
        "def comp_loss(self):\n"
        '    """Joule losses"""\n'
        "    if self.parent.parent is None:\n"
        '        raise ValueError("in an Output")\n'
        "    else:\n"
        "        output = self.parent.parent.parent\n"
        "    T_op = self.parent.Tsta\n"
        "    return output.elec, T_op\n"
    )
    package = "pyleecan.Methods_new.loss.LossModelJoule"
    result = add_container_arguments(source, package, "LossModelJoule", LOSS_GEN_DICT)
    ast.parse(result)
    assert "def comp_loss(self, loss=None, output=None):\n" in result
    assert '    output = container_or_parent(self, output, "output", depth=3)\n' in result
    assert '    loss = container_or_parent(self, loss, "loss")\n' in result
    assert "    if output is None and self.parent.parent is None:\n" in result
    assert "    else:\n        pass\n" in result
    assert "    T_op = loss.Tsta\n" in result
    assert add_container_arguments(result, package, "LossModelJoule", LOSS_GEN_DICT) == result


def test_loop_receivers():
    """Loss.comp_all_losses passes itself and its output to its models."""
    source = (
        "def comp_all_losses(self):\n"
        "    output = self.parent.parent\n"
        "    for key, model in self.model_dict.items():\n"
        "        P, f = model.comp_loss(meshsol=None)\n"
        "    for model in self.model_dict.values():\n"
        "        model.comp_loss_freq()\n"
    )
    result = add_container_arguments(source, "pyleecan.Methods_new.loss.Loss", "Loss", LOSS_GEN_DICT)
    assert "model.comp_loss(meshsol=None, loss=self, output=output)" in result
    assert "model.comp_loss_freq(loss=self, output=output)" in result
