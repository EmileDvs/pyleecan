from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv

from ....Classes_new.mesh_solution import MeshSolution


def get_arrows_plt(
    mesh_pv: pv.UnstructuredGrid,
    field: np.ndarray,
    meshsol: MeshSolution,
    factor: float,
    is_point_arrow: bool,
    phase: complex = 1 + 0j,
) -> Tuple[pv.PolyData, float]:
    """Create a pyvista arrow plot

    Parameters
    ----------
    mesh_pv : UnstructuredGrid
        a pyvista mesh object
    field : ndarray
        a vector field to plot as glyph
    meshsol : MeshSolution
        a MeshSolution object
    factor : float
        an amplitude factor for the glyph plot
    is_point_arrow : bool
        True to plot arrows on the nodes
    phase : complex
        a phase shift to apply on the plot

    Returns
    -------
    arrows_plt : PolyData
        a pyvista object to plot glyph
    factor : float
        an amplitude factor for the plot glyph
    """

    vect_field = np.real(field * phase)

    # Compute default factor if needed
    if factor is None:
        factor = 0.2 * np.max(np.abs(mesh_pv.bounds)) / np.max(np.abs(vect_field))

    # Add third dimension if needed
    solution = meshsol.get_solution()
    if solution.dimension == 2:
        vect_field = np.hstack((vect_field, np.zeros((vect_field.shape[0], 1))))

    # Add field to mesh
    if is_point_arrow:
        mesh_pv.vectors = vect_field * factor
        arrows_plt = mesh_pv.arrows
    else:
        mesh_pv["field"] = vect_field
        mesh_cell = mesh_pv.point_data_to_cell_data()
        surf = mesh_cell.extract_geometry()
        centers2 = surf.cell_centers()
        centers2.vectors = surf["field"] * factor
        arrows_plt = centers2.arrows

    return arrows_plt, factor
