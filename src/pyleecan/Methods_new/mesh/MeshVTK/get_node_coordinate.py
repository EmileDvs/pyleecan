import numpy as np
from typing import Optional



def get_node_coordinate(self, indices: Optional[np.typing.ArrayLike] = None) -> np.ndarray:
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

    mesh = self.get_mesh_pv(indices=indices)

    return mesh.points
