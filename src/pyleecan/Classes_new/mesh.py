# Experimental dataclass generated from Generator/ClassesRef/Mesh/Mesh.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from ._pyleecan_class import PyleecanClass
from .mesh_solution import MeshSolution


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

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (MeshSolution,)):
            raise TypeError(
                "Mesh parent must be an instance of MeshSolution, or None; "
                + f"got {type(parent).__name__}"
            )

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
