# Experimental dataclass generated from Generator/ClassesRef/Mesh/ElementMat.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np

from ._pyleecan_class import PyleecanClass
from .gauss_point import GaussPoint
from .ref_element import RefElement
from .scalar_product_l2 import ScalarProductL2


@dataclass(eq=False)
class ElementMat(PyleecanClass):
    """Define the connectivity under matricial format containing one type of element (example: only triangles with 3 nodes).

    Attributes
    ----------
    connectivity : ndarray or None
        Matrix of connectivity for one element type
        Default: None
    nb_element : int
        Total number of elements
        Default: 0
    nb_node_per_element : int
        Define the number of node per element
        Default: 0
    indice : ndarray or None
        Element indices
        Default: None
    ref_element : RefElement or None
        No description provided.
        Default: None
    gauss_point : GaussPoint or None
        No description provided.
        Default: None
    scalar_product : ScalarProductL2 or None
        No description provided.
        Default: ScalarProductL2()
    """

    connectivity: np.ndarray | None = None
    """Matrix of connectivity for one element type"""
    nb_element: int = 0
    """Total number of elements"""
    nb_node_per_element: int = 0
    """Define the number of node per element"""
    indice: np.ndarray | None = None
    """Element indices"""
    ref_element: RefElement | None = field(
        default=None, metadata={"default_class": "RefElement"}
    )
    gauss_point: GaussPoint | None = field(
        default=None, metadata={"default_class": "GaussPoint"}
    )
    scalar_product: ScalarProductL2 | None = field(
        default_factory=lambda: ScalarProductL2(),
        metadata={"default_class": "ScalarProductL2"},
    )

    # Inlined from Methods.Mesh.ElementMat.add_element
    def add_element(
        self, node_indices: Union[np.typing.ArrayLike, int], new_index: int
    ) -> bool:
        """Add a new element defined by node indices

        Parameters
        ----------
        self : ElementMat
            a ElementMat object
        node_indices : ndarray or list of int
            a ndarray of nodes indices (length must match self.nb_node_per_element)
        new_index : int
            Index of the new element to use

        Returns
        -------
        is_created : bool
            False if the element already exist or if it is not possible to add the element
        """

        # Check that there is the correct number of nodes
        if len(np.unique(node_indices)) != self.nb_node_per_element:
            return False

        # Check if the Element with these nodes already exist (The order of nodes indices does not matter)
        if self.is_exist(node_indices):
            return False

        # Create/Add the new element
        if self.nb_element == 0:  # First element
            # Force connectivity to have shape nb_element × nb_node_per_element
            if isinstance(node_indices, int):
                self.connectivity = np.array([[node_indices]])
            else:
                self.connectivity = np.array([node_indices])

            self.indice = np.array([new_index])
        else:
            self.connectivity = np.vstack([self.connectivity, node_indices])
            self.indice = np.concatenate([self.indice, np.array([new_index])])

        self.nb_element += 1

        return True

    # Inlined from Methods.Mesh.ElementMat.get_connectivity
    def get_connectivity(
        self, element_index: Optional[int] = None
    ) -> Union[np.ndarray, None]:
        """_summary_

        Parameters
        ----------
        self : ElementMat
            an ElementMat object
        element_index : Optional[int], optional
           the indice of a element, by default None. If None, return all elements.

        Returns
        -------
        Union[np.ndarray, None]
            Selected element connectivity. Return None if the index does not exist
        """

        connectivity = self.connectivity
        indices = self.indice
        nb_element = self.nb_element

        if element_index is None:  # Return all elements
            return connectivity

        if nb_element == 0:  # No element
            return np.array([[]])

        connectivity_index = (indices == element_index).nonzero()[0]
        if connectivity_index.size > 0:
            return connectivity[connectivity_index[0], :]
        else:
            return np.array([[]])

    # Inlined from Methods.Mesh.ElementMat.get_node2element
    def get_node2element(self, node_indice: int) -> np.ndarray:
        """Return all indices of elements containing a node.

        Parameters
        ----------
        self : ElementMat
            an ElementMat object
        node_indice : int
            a node indice

        Returns
        -------
        node_to_element: ndarray
            Indices of elements containing the node

        """

        node_to_element = np.array([], dtype=int)
        connect = self.connectivity

        if connect is None:
            return node_to_element

        if len(connect.shape) > 1:  # If there is more than 1 element
            idx_elem = (connect == node_indice).nonzero()[0]
            node_to_element = self.indice[idx_elem]

        elif sum(connect == node_indice) > 0:
            node_to_element = self.indice

        return node_to_element

    # Inlined from Methods.Mesh.ElementMat.interpolate
    def interpolate(
        self, point: np.ndarray, node_coord: np.ndarray, field: np.ndarray
    ) -> np.ndarray:
        """Return interpolated value of the field in a element

        Parameters
        ----------
        self : ElementMat
             an ElementMat object
        points : ndarray
            evaluation points
        node_coord : ndarray
            coordinates of the element nodes
        field : ndarray
            field to interpolate

        Returns
        -------
        value: array
            interpolated field

        """
        return self.ref_element.interpolation(
            point=point, node_coord=node_coord, field=field
        )

    # Inlined from Methods.Mesh.ElementMat.is_exist
    def is_exist(self, connectivity: np.ndarray) -> bool:
        """Check the existence of a element defined by a connectivity (vector of points indices).
        The order of points indices does not matter.

        Parameters
        ----------
        self : ElementMat
            an ElementMat object
        connectivity : ndarray
            an array of node tags

        Returns
        -------
            bool
                True if the element already exist
        """
        if self.nb_node_per_element > 3:
            self.get_logger().warning(
                "ElementMat.is_exist doesn't take into account quad node permutations."
            )

        # Check if the element connectivity provided has the good size
        if self.nb_node_per_element != len(connectivity):
            return False

        # Get the element index for each node of the connectivity
        node_element = np.concatenate(
            [self.get_node2element(node_index) for node_index in connectivity],
        )

        # Count how many nodes of each element are present in the connectivity
        _, unique_counts = np.unique(node_element, return_counts=True)

        # The element already exist if all its node are present in the given connectivity
        result = np.any(unique_counts == self.nb_node_per_element)

        return result
