from ....classes_common.functions import legacy_function_source


def _set_keeper(self, value) -> None:
    """setter of keeper

    A callable, the source of a lambda (numpy usable as np, sqrt and pi), the
    path to a python file (with a wildcard: "<PARAM_DIR>/keeper.py") or a path
    in the simulation ("simu.machine.rotor.slot.W0", as the legacy setter).
    The field keeps the function with its source (SourceFunction, saved by
    its source).

    Parameters
    ----------
    self : DataKeeper
        A DataKeeper object
    value : callable or str or None
        Function extracting the kept data from an output
    """
    self.keeper = legacy_function_source(value, "setter")
