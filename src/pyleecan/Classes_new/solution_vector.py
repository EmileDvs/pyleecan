# Experimental dataclass generated from Generator/ClassesRef/Mesh/SolutionVector.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from dataclasses import field as dataclass_field

import numpy as np

from .data_1d import Data1D
from .solution import Solution
from .vector_field import VectorField


@dataclass(eq=False)
class SolutionVector(Solution):
    """Define a Solution with SciDataTool objects.

    Attributes
    ----------
    field : VectorField or None
        Data object containing the numerical values of a solution. One of the axis must be "Indices", a list of indices. If the solution is a vector, one of the axis must be "Direction", values ['x','y'] for example.
        Default: None
    """

    field: VectorField | None = dataclass_field(
        default=None, metadata={"default_class": "VectorField"}
    )
    """Data object containing the numerical values of a solution. One of the axis must be "Indices", a list of indices. If the solution is a vector, one of the axis must be "Direction", values [\'x\',\'y\'] for example."""

    # Inlined from Methods.Mesh.SolutionVector.get_axes_list
    def get_axes_list(self, *args):
        """Get the axis of variables stored in Solution.

        Parameters
        ----------
        self : SolutionVector
            an SolutionVector object
        field_name : str
            name of the field to return

        Returns
        -------
        field: array
            an array of field values

        """

        # Build axis list
        ax_name = []
        ax_size = []

        axes = self.field.get_axes(*args)

        if "comp_x" in self.field.components:
            comp = self.field.components["comp_x"]
        elif "radial" in self.field.components:
            comp = self.field.components["radial"]
        else:
            raise Exception(
                "self.field.components shall have either comp_x or radial key"
            )

        for axis in axes:
            ax_name.append(axis.name)
            ax_size.append(axis.get_length())

        ax_name.append("component")
        ax_size.append(len(self.field.components))

        return ax_name, ax_size

    # Inlined from Methods.Mesh.SolutionVector.get_field
    def get_field(self, *args, is_squeeze=False, node=None, is_rthetaz=False):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : SolutionVector
            an SolutionVector object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        nodes : array of float
            Node of the mesh (optional)
        is_rthetaz : bool
            cylindrical coordinates

        Returns
        -------
        field: array
            an array of field values

        """
        # if len(args) == 1 and type(args[0]) == tuple:
        #     args = args[0]

        if is_squeeze:
            axname, axsize = self.get_axes_list(*args)
        else:
            axname, axsize = self.get_axes_list()

        components = self.field.components
        ind_0 = axname.index("component")

        field_list = []
        if "comp_x" in components:
            results = self.field.get_xyz_along(args, is_squeeze=is_squeeze)

            if "comp_x" in results:
                field_list.append(results["comp_x"])

            if "comp_y" in results:
                field_list.append(results["comp_y"])

            if "comp_z" in results and self.dimension == 3:
                field_list.append(results["comp_z"])

        else:
            results = self.field.get_rphiz_along(args, is_squeeze=is_squeeze)

            if "radial" in results:
                field_list.append(results["radial"])

            if "axial" in results and self.dimension == 3:
                field_list.append(results["axial"])

            # if "circ" in results:
            #     field_dict["1"] = results["circ"]

            if "tangential" in results:
                field_list.append(results["tangential"])

        field = np.array(field_list)
        field = np.moveaxis(field, 0, ind_0)

        return field

    # Inlined from Methods.Mesh.SolutionVector.get_solution
    def get_solution(self, indice=None):
        """Return a copy of the solution with the option to only include specified indices.

        Parameters
        ----------
        self : SolutionVector
            a SolutionVector object
        indices : list
            list of indices, if list is empty or None all indices are included

        Returns
        -------
        solution: SolutionMat
            solution

        """
        logger = self.get_logger()

        # create copy to directly manipulate data
        solution = self.copy()

        if indice:
            for field in solution.field.components.values():
                # get axes data
                axes = field.axes
                axes_names = [axis.name for axis in field.axes]
                ax_idx = axes_names.index("indice")

                org_indice = axes[ax_idx].get_values()

                if set(indice) - set(org_indice):
                    logger.warning(
                        "At least one input indice is not part of the solution. "
                        + "Respective indice will be skipped."
                    )

                # skip indice that are not part of the solution
                new_indice = [ii for ii in indice if ii in org_indice]

                # create requested axes list to get field values (see SciDataTool ref.)
                args = [
                    name + "[smallestperiod]" if name != "indice" else name
                    for name in axes_names
                ]
                args[ax_idx] += "=axis_data"

                # get the field values
                field_dict = field.get_along(*args, axis_data={"indice": new_indice})

                # set new indice axis
                axes[ax_idx] = Data1D(
                    values=new_indice,
                    is_components=axes[ax_idx].is_components,
                    symmetries=axes[ax_idx].symmetries,
                    symbol=axes[ax_idx].symbol,
                    name=axes[ax_idx].name,
                    unit=axes[ax_idx].unit,
                    normalizations=axes[ax_idx].normalizations,
                )

                # set new field data
                field.values = field_dict[field.symbol]

        return solution
