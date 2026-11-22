# Experimental dataclass generated from Generator/ClassesRef/Simulation/ParamExplorerSet.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, ClassVar

from .param_explorer import ParamExplorer


@dataclass(eq=False)
class ParamExplorerSet(ParamExplorer):
    """Define a parameter set (for parameter sweep) from a list

    Attributes
    ----------
    value : [] or None
        List containing the different parameter values to explore
        Default: []
    """

    value: list[Any] = field(default_factory=list)
    """List containing the different parameter values to explore"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.ParamExplorerSet.get_max
    def get_max(self) -> float | None:
        """Return the maximum value of the ParamExplorer

        Parameters
        ----------
        self : ParamExplorerInterval
            A ParamExplorerInterval object

        Returns
        -------
        max_value: float
            Maximum value of the ParamExplorer
        """

        if len(self.value) > 0 and isinstance(self.value[0], (int, float)):
            return max(self.value)
        else:
            return None

    # Inlined from Methods.Simulation.ParamExplorerSet.get_min
    def get_min(self) -> float | None:
        """Return the minimum value of the ParamExplorer

        Parameters
        ----------
        self : ParamExplorerInterval
            A ParamExplorerInterval object

        Returns
        -------
        min_value: float
            Minimum value of the ParamExplorer
        """

        if len(self.value) > 0 and isinstance(self.value[0], (int, float)):
            return min(self.value)
        else:
            return None

    # Inlined from Methods.Simulation.ParamExplorerSet.get_N
    def get_N(self) -> int:
        """Return the number of value of the ParamExplorer

        Parameters
        ----------
        self : ParamExplorerInterval
            A ParamExplorerInterval object

        Returns
        -------
        N: int
            number of value of the ParamExplorer
        """

        return len(self.value)

    # Inlined from Methods.Simulation.ParamExplorerSet.get_value
    def get_value(self):
        """Return parameters values"""
        return self.value
