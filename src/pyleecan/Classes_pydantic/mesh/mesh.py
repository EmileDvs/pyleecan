# Experimental pydantic model generated from Generator/ClassesRef/Mesh/Mesh.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar, Optional

import numpy as np
from pydantic import Field

from .._legacy_model import LegacyModel


class Mesh(LegacyModel):
    """Abstract Class for mesh related classes

    Attributes
    ----------
    dimension : int
        Dimension of the physical problem
        Default: 2; Minimum: 1; Maximum: 3
    """

    dimension: int = Field(default=2, ge=1, le=3)
    """Dimension of the physical problem"""

    _package: ClassVar[str] = "Mesh"
    """Name of the package of the legacy class module"""

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
