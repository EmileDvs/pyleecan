# Experimental dataclass generated from Generator/ClassesRef/Mesh/SolutionMat.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

import numpy as np

from .solution import Solution


@dataclass(eq=False)
class SolutionMat(Solution):
    """Define a Solution with ndarray object.

    Attributes
    ----------
    field : ndarray or None
        Matrix/Vector of the numerical values of the solutions.
        Default: None
    indice : ndarray or None
        Indices of loaded elements. Set to None if all elements are loaded
        Default: None
    axis_name : list or None
        List of axis names (e.g. "time", "direction")
        Default: []
    axis_size : list or None
        List of axis sizes
        Default: []
    """

    field: np.ndarray | None = None
    """Matrix/Vector of the numerical values of the solutions."""
    indice: np.ndarray | None = None
    """Indices of loaded elements. Set to None if all elements are loaded"""
    axis_name: list[Any] | None = dataclass_field(default_factory=list)
    """List of axis names (e.g. "time", "direction")"""
    axis_size: list[Any] | None = dataclass_field(default_factory=list)
    """List of axis sizes"""

    # Inlined from Methods.Mesh.SolutionMat.get_axes_list
    def get_axes_list(self, *args):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : SolutionMat
            an SolutionMat object

        Returns
        -------
        axis_dict: list
            a list of axis names containing axis sizes

        """

        if self.axis_name is not None:
            axis_name = self.axis_name.copy()
        else:
            axis_name = None

        if self.axis_size is not None:
            axis_size = self.axis_size.copy()
        else:
            axis_size = None

        return axis_name, axis_size

    # Inlined from Methods.Mesh.SolutionMat.get_field
    def get_field(self, *args, is_squeeze=False, node=None, is_rthetaz=False):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : Solution
            an Solution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        is_squeeze : boolean
            To numpy.squeeze the output ndarray

        Returns
        -------
        field_new: ndarray
            an ndarray of field values sliced according to args.

        """
        if args is None:
            args = {}
        else:
            if len(args) == 1 and type(args[0]) == tuple:
                args = args[0]

        field_new = self.field.copy()

        if len(args) > 0:
            if self.axis_name is not None:
                nb_axis = len(self.axis_name)
                for i in range(nb_axis):
                    # ax = np.where(np.array(field.shape) == self.axis_size[i])[0][0]
                    ax_name = self.axis_name[i]
                    is_found = False
                    for axis_str in args:
                        if ax_name in axis_str:
                            is_found = True
                            if "[" in axis_str:
                                elems = axis_str.split("[")
                                ind_str = elems[1].strip("]")

                                # Range of indices
                                if ":" in ind_str:
                                    elems2 = ind_str.split(":")
                                    indices = [
                                        i
                                        for i in range(
                                            int(elems2[0]), int(elems2[1]) + 1
                                        )
                                    ]
                                # List of indices
                                elif "," in ind_str:
                                    indices = [int(x) for x in ind_str.split(",")]
                                # Single index
                                else:
                                    indices = [int(ind_str)]

                                field_new = np.take(field_new, indices=indices, axis=i)

                    if not is_found:
                        field_new = np.take(field_new, indices=0, axis=i)
                        field_new = np.expand_dims(field_new, i)

        if is_squeeze:
            field_new = np.squeeze(field_new)

        return field_new

    # Inlined from Methods.Mesh.SolutionMat.get_solution
    def get_solution(self, indice=None):
        """Return a copy of the solution with the option to only include specified indices.

        Parameters
        ----------
        self : SolutionMat
            a SolutionMat object
        indices : list
            list of indices, if list is empty or None all indices are included

        Returns
        -------
        solution: SolutionMat
            solution

        """
        logger = self.get_logger()

        field_sol = self.get_field()
        axis_name, axis_size = self.get_axes_list()
        s_indice = self.indice

        Iindice = axis_name.index("indice")

        # create indices of solution if None
        if s_indice is None:
            s_indice = [i for i in range(field_sol.shape[Iindice])]

        # check input indices
        if not indice:
            indice = s_indice

        if set(indice) - set(s_indice):
            logger.warning(
                "At least one input indice is not part of the solution. "
                + "Respective indice will be skipped."
            )

        # skip indice that are not part of the solution
        new_indice = [ii for ii in indice if ii in s_indice]

        # get array index of new_indice
        array_indice = [np.where(np.array(s_indice) == ii)[0][0] for ii in new_indice]

        # setup requested solution
        axis_size[Iindice] = len(new_indice)
        new_field_sol = np.take(field_sol, array_indice, axis=Iindice)

        solution = type(self)(
            label=self.label,
            type_element=self.type_element,
            field=new_field_sol,
            indice=indice,
            axis_name=axis_name,
            axis_size=axis_size,
            dimension=self.dimension,
        )

        return solution
