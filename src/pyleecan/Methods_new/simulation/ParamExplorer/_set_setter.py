from ....classes_common.functions import legacy_function_source


def _set_setter(self, value) -> None:
    """setter of setter

    A callable, the source of a lambda, the path to a python file (with a
    wildcard: "<PARAM_DIR>/setter_rotor.py") or a path in the simulation
    ("simu.machine.rotor.slot.W0": the lambda setting it). The field keeps the
    function with its source (SourceFunction, saved by its source).

    Parameters
    ----------
    self : ParamExplorer
        A ParamExplorer object
    value : callable or str or None
        Setter of the parameter
    """
    self.setter = legacy_function_source(value, "setter")
