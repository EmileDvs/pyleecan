from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_element_area(self, indices: list | None = None) -> np.ndarray:
    """Return the area of the elements on the outer surface.

    Parameters
    ----------
    self : MeshVTK
        a MeshVTK object
    indices : list
        list of the points to extract (optional)

    Returns
    -------
    areas: ndarray
        Area of the elements
    """

    surf = self.get_surf(indices=indices)

    return surf.compute_element_sizes(area=True)["Area"]
