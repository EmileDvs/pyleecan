# Experimental dataclass generated from Generator/ClassesRef/Simulation/ParamExplorerInterval.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .param_explorer import ParamExplorer


@dataclass(eq=False)
class ParamExplorerInterval(ParamExplorer):
    """Define a set of value (for parameter sweep) on interval

    Attributes
    ----------
    min_value : float
        Minumum value of the interval
        Default: 0
    max_value : float
        Maximum value of the interval
        Default: 1
    N : int
        Number of value to take in the interval
        Default: 4; Minimum: 2
    type_value_gen : int
        How to generate the value list. 0: linspace, 1: random (Not available yet)
        Default: 0; Minimum: 0; Maximum: 1
    type_value : int
        Type of the value: 0:float, 1:int
        Default: 0; Minimum: 0; Maximum: 1
    """

    min_value: float = 0
    """Minumum value of the interval"""
    max_value: float = 1
    """Maximum value of the interval"""
    N: int = 4
    """Number of value to take in the interval"""
    type_value_gen: int = 0
    """How to generate the value list. 0: linspace, 1: random (Not available yet)"""
    type_value: int = 0
    """Type of the value: 0:float, 1:int"""

    # Inlined from Methods.Simulation.ParamExplorerInterval.get_max
    def get_max(self):
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

        if self.type_value == 0:  # float
            return self.max_value
        else:
            return int(self.max_value)

    # Inlined from Methods.Simulation.ParamExplorerInterval.get_min
    def get_min(self):
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

        if self.type_value == 0:  # float
            return self.min_value
        else:
            return int(self.min_value)

    # Inlined from Methods.Simulation.ParamExplorerInterval.get_N
    def get_N(self):
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

        return self.N

    # Inlined from Methods.Simulation.ParamExplorerInterval.get_value
    def get_value(self):
        """Return parameters values"""
        assert self.min_value < self.max_value

        if self.type_value_gen == 0:  # linspace
            if self.type_value == 0:
                dtype = float
            elif self.type_value == 1:
                dtype = int
            value = np.linspace(
                start=self.min_value,
                stop=self.max_value,
                num=self.N,
                endpoint=True,
                dtype=dtype,
            )
            value.tolist()
        return value
