# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/RefElement.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._pyleecan_class import PyleecanClass
from .element_mat import ElementMat


@dataclass(eq=False)
class RefElement(PyleecanClass):
    """Store shape functions definition in the reference element

    Attributes
    ----------
    epsilon : float
        Precision criterion
        Default: 0.05; Minimum: 0.00E+00
    """

    epsilon: float = 0.05
    """Precision criterion"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (ElementMat,)):
            raise TypeError(
                "RefElement parent must be an instance of ElementMat, or None; "
                + f"got {type(parent).__name__}"
            )

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
