from ....classes_common.functions import legacy_function_source


def _set_getter(self, value) -> None:
    """setter of getter

    A callable, the source of a lambda, the path to a python file (with a
    wildcard: "<PARAM_DIR>/getter_rotor.py") or a path in the simulation
    ("simu.machine.rotor.slot.W0": the lambda reading it). The field keeps the
    function with its source (SourceFunction, saved by its source).

    Parameters
    ----------
    self : ParamExplorer
        A ParamExplorer object
    value : callable or str or None
        Getter of the parameter
    """
    self.getter = legacy_function_source(value, "getter")
