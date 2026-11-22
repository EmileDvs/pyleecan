# Experimental dataclass generated from Generator/ClassesRef/Mesh/Mesh.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Optional

import numpy as np

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class Mesh(LegacyClass):
    """Abstract Class for mesh related classes

    Attributes
    ----------
    dimension : int
        Dimension of the physical problem
        Default: 2; Minimum: 1; Maximum: 3
    """

    dimension: int = field(default=2, metadata={"min": 1, "max": 3})
    """Dimension of the physical problem"""

    _package: ClassVar[str] = "Mesh"
    """Name of the package of the legacy class module"""

    if TYPE_CHECKING:
        # Members of the daughter classes, for the type checkers
        # (not defined at runtime: no field, no method)

        def get_element_area(self, *args: Any, **kwargs: Any) -> np.ndarray: ...

        @property
        def element_dict(self) -> dict[str, Any]: ...
        @element_dict.setter
        def element_dict(self, value: dict[str, Any]) -> None: ...

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
