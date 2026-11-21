"""Loggers without the parent chain (PLAN.md Step 9)."""

import ast

from pyleecan.classes_common.logger_context import get_logger, logger_context
from pyleecan.Generator.ClassGenerator.New.modernize import redirect_get_logger, wrap_logger_context
from pyleecan.loggers import DEFAULT_LOG_NAME


class Obj:
    def __init__(self, logger_name=None, parent=None):
        if logger_name is not None:
            self.logger_name = logger_name
        self.parent = parent


def test_get_logger_order():
    """Own logger_name, then the simulation in progress, then parents, then default."""
    assert get_logger(Obj("Pyleecan.Own")).name == "Pyleecan.Own"
    assert get_logger(Obj()).name == DEFAULT_LOG_NAME
    assert get_logger(None).name == DEFAULT_LOG_NAME
    simu = Obj()
    with logger_context(simu):
        simu.logger_name = "Pyleecan.Simu"  # Set after the context (init_logger)
        assert get_logger(Obj()).name == "Pyleecan.Simu"
        assert get_logger(Obj("Pyleecan.Own")).name == "Pyleecan.Own"
        with logger_context(Obj("Pyleecan.Sub")):  # Nested simulation
            assert get_logger(Obj()).name == "Pyleecan.Sub"
        assert get_logger(Obj()).name == "Pyleecan.Simu"
    # Legacy layer: the parents, out of a simulation
    assert get_logger(Obj(parent=Obj(parent=Obj("Pyleecan.Machine")))).name == "Pyleecan.Machine"


def test_redirect_get_logger():
    source = (
        '"""Doc"""\n\n'
        "def comp(self, output):\n"
        "    self.get_logger().info('a')\n"
        "    output.mag.get_logger().debug('b')\n"
    )
    result = redirect_get_logger(source, "pyleecan.Methods_new.machine.Lamination")
    assert result.startswith('"""Doc"""\nfrom ....classes_common.logger_context import get_logger\n')
    assert "    get_logger(self).info('a')\n" in result
    assert "    get_logger(output.mag).debug('b')\n" in result
    assert redirect_get_logger(result, "pyleecan.Methods_new.machine.Lamination") == result
    legacy = "from ...Functions.get_logger import get_logger\n\n\ndef f(obj):\n    get_logger(obj).info('x')\n"
    result = redirect_get_logger(legacy, "pyleecan.Functions.FEMM")
    assert "from ...classes_common.logger_context import get_logger\n" in result
    assert "Functions.get_logger" not in result


def test_wrap_logger_context():
    source = (
        "def run(self):\n"
        '    """Run"""\n'
        "    # In-function import to avoid ImportError\n"
        "    from ....Classes.Output import Output\n\n"
        "    return Output()\n"
    )
    result = wrap_logger_context(source, "pyleecan.Methods_new.simulation.Simulation", "run")
    ast.parse(result)
    assert (
        "    with logger_context(self):\n"
        "        # In-function import to avoid ImportError\n"
        "        from ....Classes.Output import Output\n"
    ) in result
    assert wrap_logger_context(result, "pyleecan.Methods_new.simulation.Simulation", "run") == result
