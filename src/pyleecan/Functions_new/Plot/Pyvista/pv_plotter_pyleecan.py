"""Interface of pyleecan with FEMM (pv_plotter_pyleecan), written by the functions
generator from the modules of Functions/Plot.Pyvista (PLAN.md Step 8).
"""

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pyvista as pv
import pyvista.plotting  # noqa: F401 (loaded on demand)

from ....definitions import config_dict

FONT_FAMILY_PYVISTA = config_dict["PLOT"]["FONT_FAMILY_PYVISTA"]


COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]


COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]


COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]


class pv_plotter_pyleecan:
    """Plots of pyleecan with PyVista: the PyVista functions of pyleecan

    Static methods for now (configure_plot creates the plotter): the object
    gathers the functions, to be improved later (PLAN.md Step 8).
    """

    @staticmethod
    def configure_plot(
        pv_plotter: Optional[pv.plotting.BasePlotter],
        win_title: str,
        is_show_axes: bool = True,
    ) -> Tuple[pv.plotting.BasePlotter, Dict[str, Any]]:
        """Configure a pyvista plot. If the plotter doesn't exist, create one depending on available package: PyVista or PyVistaQt.

        Parameters
        ----------
        pv_plotter : pyvista plotter
            a pyvista plotter
        win_title : str
            title of the window
        save_path : str
            path where to save the plot
        """

        if pv_plotter is None:
            # Instantiate pv_plotter
            pv_plotter = pv.plotting.Plotter(
                notebook=False,
                title=win_title,
                theme=pv.plotting.themes.DocumentTheme(),
            )

        # isometric view with z towards left
        pv_plotter.view_isometric()

        if is_show_axes:
            pv_plotter.add_axes(
                color="k", x_color="#da3061", y_color="#0069a1", z_color="#bbcf1c"
            )
        sargs = dict(
            interactive=True,
            title_font_size=12,
            label_font_size=10,
            font_family=FONT_FAMILY_PYVISTA,
            color="black",
        )

        return pv_plotter, sargs

    @staticmethod
    def plot_glyph_pv(
        pv_plotter: Any,
        mesh_pv: pv.UnstructuredGrid,
        vect_field: np.ndarray,
        is_point_arrow: bool,
        factor: float = 1,
        phase: complex = 1,
    ) -> None:
        """Plot a vector field as arrow (or glyph) using pyvista plotter.

        Parameters
        ----------
        pv_plotter : pyvista.Plotter
            a pyvista plotting object
        mesh_pv : UnstructuredGrid
            a pyvista mesh object
        vect_field : ndaray
            field to plot
        is_point_arrow : bool
            True to plot arrows on the nodes
        factor : float
            amplitude factor for vector field
        phase : complex
            coefficient to change the phase of the plot

        Returns
        -------
        """

        field = np.real(vect_field * factor * phase)
        is_nodal_sol = field.shape[0] == mesh_pv.n_points

        # Add field to mesh
        if is_nodal_sol:
            mesh_pv.point_data["field_to_plot"] = field
            mesh_pv.set_active_vectors("field_to_plot", "point")
            if is_point_arrow:
                arrows_plt = mesh_pv.arrows
            else:
                # Convert point_data to cell data
                mesh_cell = mesh_pv.point_data_to_cell_data()
                surf = mesh_cell.extract_geometry()
                centers2 = surf.cell_centers()
                centers2.vectors = surf["field_to_plot"]
                arrows_plt = centers2.arrows

        else:
            mesh_pv.cell_data["field_to_plot"] = field
            mesh_pv.active_vectors_name = "field_to_plot"
            if is_point_arrow:
                mesh_node = mesh_pv.cell_data_to_point_data()
                mesh_node.set_active_vectors("field_to_plot", "cell")
                arrows_plt = mesh_node.arrows

            else:
                cell_centers = mesh_pv.cell_centers()
                cell_centers.set_active_vectors("field_to_plot", "cell")
                arrows_plt = cell_centers.arrows

        pv_plotter.add_mesh(arrows_plt, color="red")

    @staticmethod
    def plot_mesh_field(
        pv_plotter: Any,
        sargs: dict,
        field_name: str,
        clim: list | None = None,
        mesh_pv: Any | None = None,
        field: np.ndarray | None = None,
        phase: complex = 1,
        colormap: str = COLOR_MAP,
    ) -> None:
        mesh_pv[field_name] = np.real(field * phase)
        mesh_field = mesh_pv

        pv_plotter.add_mesh(
            mesh_field,
            scalars=field_name,
            show_edges=False,
            cmap=colormap,
            clim=clim,
            scalar_bar_args=sargs,
        )

    @staticmethod
    def plot_surf_deflection(
        pv_plotter: Any,
        sargs: dict,
        surf_pv: Any,
        vect_field: np.ndarray,
        field: np.ndarray,
        field_name: str,
        clim: list | None = None,
        factor: float | None = None,
        phase: complex = 1,
    ) -> None:
        """Plot a vector field as arrow (or glyph) using pyvista plotter.

        Parameters
        ----------
        pv_plotter : pyvista.Plotter
            a pyvista plotting object
        *sargs: list of strings
            List of arguments for the scalar bar
        surf_pv : UnstructuredGrid
            a pyvista surface mesh object
        vect_field : ndaray
            field to plot
        field : ndarray
            a vector field to plot as glyph
        field_name : str
            name of the field
        clim : list
            a list of 2 elements for the limits of the colorbar
        factor : float
            amplitude factor for vector field
        phase : complex
            coefficient to change the phase of the plot

        Returns
        -------
        """

        # Compute colorbar boundaries
        if clim is None:
            clim = [np.min(np.real(field)), np.max(np.real(field))]
            if (clim[1] - clim[0]) / clim[1] < 0.01:
                clim[0] = -abs(clim[1])
                clim[1] = abs(clim[1])

        # Compute deformation factor
        if factor is None:
            factor = 0.2 * np.max(np.abs(surf_pv.bounds)) / np.max(np.abs(vect_field))

        # Compute pyvista object
        # Add field to surf
        surf_pv.point_data[field_name] = np.real(vect_field * phase) * factor
        surf_pv.active_vectors_name = field_name

        # Warp by vectors
        surf_warp = surf_pv.warp_by_vector()

        # Add normal field amplitude for colormap
        surf_warp[field_name] = np.real(field * phase)

        # Plot mesh
        pv_plotter.add_mesh(
            surf_pv, color="grey", opacity=0.7, show_edges=True, edge_color="white"
        )

        # Plot deflection
        pv_plotter.add_mesh(
            surf_warp,
            scalars=field_name,
            opacity=1,
            show_edges=False,
            cmap=COLOR_MAP,
            clim=clim,
            scalar_bar_args=sargs,
        )
