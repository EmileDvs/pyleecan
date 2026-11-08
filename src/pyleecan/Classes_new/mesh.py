# Experimental dataclass generated from Generator/ClassesRef/Mesh/Mesh.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Mesh(PyleecanClass):
    """Abstract Class for mesh related classes

    Attributes
    ----------
    dimension : int
        Dimension of the physical problem
        Default: 2; Minimum: 1; Maximum: 3
    """

    dimension: int = 2
    """Dimension of the physical problem"""

    # Inlined from Methods.Mesh.Mesh.get_node_coordinate
    def get_node_coordinate(
        self, indices: Optional[np.typing.ArrayLike] = None
    ) -> np.ndarray:
        """Return the coordinates of the node with provided indices.
        If indices is not specified, returns every node coordinates

        Parameters
        ----------
        indices : Optional[ArrayLike], optional
            Indices of the targeted nodes. If None, return all.

        Returns
        -------
        np.ndarray
            nodes coordinates
        """

        raise NotImplementedError("Mesh is an abstract class")
