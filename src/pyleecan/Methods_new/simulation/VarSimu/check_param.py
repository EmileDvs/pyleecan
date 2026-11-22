

class VarSimuError(Exception):
    pass


def check_param(self) -> None:
    """Check VarParamSweep parameters validity"""
    # Local import: avoids circular imports
    from ....Classes_new.simulation.simulation import Simulation

    if type(self).__name__ == "VarSimu":
        raise VarSimuError(
            "VarSimu is an abstract class, please create one of its daughters."
        )

    # Check for simulation or VarSimu
    if self.parent is None or not isinstance(self.parent, Simulation):
        raise VarSimuError("VarSimu object must be inside a Simulation object")
