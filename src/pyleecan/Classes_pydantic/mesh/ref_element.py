# Experimental pydantic model generated from Generator/ClassesRef/Mesh/Interpolation/RefElement.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np
from pydantic import Field

from .._pyleecan_model import PyleecanModel


class RefElement(PyleecanModel):
    """Store shape functions definition in the reference element

    Attributes
    ----------
    epsilon : float
        Precision criterion
        Default: 0.05; Minimum: 0.00E+00
    """

    epsilon: float = Field(default=0.05, ge=0.0)
    """Precision criterion"""

    _package: ClassVar[str] = "Mesh"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Mesh.RefElement.get_element_area
    def get_element_area(self, element_coordinate: np.ndarray) -> np.ndarray:
        """Return the area of the elements.

        Parameters
        ----------
        self : RefElement
        element_coordinate : list or array
            the elements coordinates

        Returns
        -------
        area: array
            area of the elements
        """

        raise NotImplementedError(
            f"{type(self).__name__}.get_element_area is not implemented."
        )

    # Inlined from Methods.Mesh.RefElement.interpolation
    def interpolation(
        self, point: np.ndarray, node_coord: np.ndarray, field: np.ndarray
    ) -> np.ndarray:
        """Return interpolated value of the field in a element

        Parameters
        ----------
        self : Interpolation
             an Interpolation object
        point : ndarray
            evaluation point
        node_coord : ndarray
            coordinates of the element nodes
        field : ndarray
            field to interpolate

        Returns
        -------
        value: array
            interpolated field

        """

        point_ref = self.get_ref_point(node_coord, point)
        values_ref, _ = self.shape_function(point_ref)

        interp_func = np.tensordot(values_ref, field, axes=([2], [0]))

        return interp_func
