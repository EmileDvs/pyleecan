# Experimental dataclass generated from Generator/ClassesRef/Mesh/NodeMat.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Optional, Union

import numpy as np

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class NodeMat(PyleecanClass):
    """Class to define nodes coordinates and getter.

    Attributes
    ----------
    coordinate : ndarray or None
        Nodes coordinates
        Default: None
    nb_node : int
        Total number of nodes
        Default: 0
    delta : float
        Sensibility for node searching
        Default: 1e-10
    indice : ndarray or None
        Nodes unique indices
        Default: None
    """

    coordinate: np.ndarray | None = None
    """Nodes coordinates"""
    nb_node: int = 0
    """Total number of nodes"""
    delta: float = 1e-10
    """Sensibility for node searching"""
    indice: np.ndarray | None = None
    """Nodes unique indices"""

    # Inlined from Methods.Mesh.NodeMat.add_node
    def add_node(self, coordinate: np.typing.ArrayLike) -> Union[None, int]:
        """Add a new node defined by its coordinates to the NodeMat
        (if a node of this coordinate already exist, do nothing)

        Parameters
        ----------
        self : NodeMat
            an NodeMat object
        coordinate : ArrayLike
            The list of coordinates (length must match mesh dimension)

        Returns
        -------
        Union[None,int]
            Index of the new node or None if the node already exists
        """
        if self.is_exist(coordinate):
            return None

        # Empty coordinate case
        if self.coordinate is None or self.coordinate.size == 0:
            self.coordinate = np.array([coordinate])
            self.nb_node = 1
            self.indice = np.array([0], dtype=np.int32)

            return 0

        # Add node only if it doesn't already exist
        self.coordinate = np.vstack((self.coordinate, coordinate))
        new_index = np.max(self.indice) + 1
        self.indice = np.concatenate((self.indice, np.array([new_index])))
        self.nb_node += 1

        return new_index

    # Inlined from Methods.Mesh.NodeMat.get_coord
    def get_coord(self, node_indices: np.typing.ArrayLike) -> np.ndarray:
        """Return the coordinates of node(s).

        Parameters
        ----------
        node_indices : ArrayLike
            Array of node indices

        Returns
        -------
        np.ndarray
            Array of node coordinates
        """

        # Extract position of the given node indices in the index vector
        coord_indices = [
            (self.indice == index).nonzero()[0][0] for index in node_indices
        ]

        return self.coordinate[coord_indices]

    # Inlined from Methods.Mesh.NodeMat.get_indice
    def get_indice(
        self, coordinate: Optional[np.ndarray] = None
    ) -> Union[np.ndarray, int]:
        """Return the coordinates of node(s).

        Parameters
        ----------
        self : NodeMat
            an NodeMat object
        coordinate : Optional[np.ndarray]
            a node coordinate

        Returns
        -------
        Union[np.ndarray, int]
            Index of the provided node coordinates or every indices
        """

        if coordinate is None:
            return self.indice

        # The distance-based method is more time-consuming, but could provide a tolerance in the search of the node.
        # Compute the distance between nodes coordinates and the given ones
        dist_node = np.linalg.norm(self.coordinate - coordinate, axis=1)
        index_min = np.argmin(dist_node)
        if dist_node[index_min] < self.delta:
            return self.indice[index_min]
        else:
            raise ValueError(
                f"The node with coordinate {coordinate} has not been retrieved with tolerance {self.delta}, increasing the tolerance value may solve the issue."
            )

    # Inlined from Methods.Mesh.NodeMat.is_exist
    def is_exist(self, coordinate: np.ndarray) -> bool:
        """Check the existence of a node defined by its coordinates

        Parameters
        ----------
        self : NodeMat
            an NodeMat object
        coordinate : ndarray
            coordinate of the node

        Returns
        -------
        bool
            True if the element already exist
        """

        if self.nb_node == 0:
            return False

        # Compute the distance between the node coordinates and the provided coordinate
        dist_node = np.linalg.norm(self.coordinate - coordinate, axis=1)

        return np.any(dist_node < self.delta)
