# Experimental dataclass generated from Generator/ClassesRef/Mesh/SolutionData.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .data_1d import Data1D
from .data_nd import DataND
from .solution import Solution


@dataclass(eq=False)
class SolutionData(Solution):
    """Define a Solution with SciDataTool objects.

    Attributes
    ----------
    field : DataND or None
        Data object containing the numerical values of a solution. One of the axis must be "Indices", a list of indices. If the solution is a vector, one of the axis must be "Direction", values ['x','y'] for example.
        Default: None
    """

    field: DataND | None = None
    """Data object containing the numerical values of a solution. One of the axis must be "Indices", a list of indices. If the solution is a vector, one of the axis must be "Direction", values [\'x\',\'y\'] for example."""

    # Inlined from Methods.Mesh.SolutionData.get_axes_list
    def get_axes_list(self, *args):
        """Get the axis of variables stored in Solution.

        Parameters
        ----------
        self : SolutionData
            an SolutionData object
        args : list
            list of SciDataTool arguments

        Returns
        -------
        field: array
            an array of field values

        """

        # Build axis list
        ax_name = []
        ax_size = []

        axes = self.field.get_axes()

        ax_name_orig = [axis.name for axis in axes]

        if len(args) == 0:
            for axis in axes:
                ax_name.append(axis.name)
                ax_size.append(axis.get_length())
        else:
            for arg in args:
                # TODO: fill missing SciDataTool syntax to return proper axis size
                if "[" in arg:
                    # Periodicities / slicing
                    arg_split = arg.split("[")
                    ax_name.append(arg_split[0])
                    ind_ax = ax_name_orig.index(ax_name[-1])
                    if "smallest" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_smallestperiod=True))
                    elif "one" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_oneperiod=True))
                    elif "anti" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_antiperiod=True))
                    else:
                        ax_size.append(len(eval(arg.split(ax_name[-1])[-1])))
                elif "=" in arg:
                    # ignore axis
                    pass
                elif "freqs" in arg and "time" in ax_name_orig:
                    # FFT
                    ax_name.append("freqs")
                    ind_ax = ax_name_orig.index("time")
                    Nt_per = axes[ind_ax].get_length(is_oneperiod=True)
                    if Nt_per % 2 == 0:
                        Nfreq = int(Nt_per / 2) + 1
                    else:
                        Nfreq = int((Nt_per - 1) / 2)
                    ax_size.append(Nfreq)
                else:
                    # No operation requested
                    ax_name.append(arg)
                    ind_ax = ax_name_orig.index(ax_name[-1])
                    ax_size.append(axes[ind_ax].get_length())

        return ax_name, ax_size

    # Inlined from Methods.Mesh.SolutionData.get_field
    def get_field(self, *args, is_squeeze=False, node=None, is_rthetaz=False):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : SolutionData
            an SolutionData object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)

        Returns
        -------
        field: array
            an array of field values

        """
        axname, _ = self.get_axes_list()
        symbol = self.field.symbol

        if len(args) == 0:
            field_dict = self.field.get_along(tuple(axname), is_squeeze=is_squeeze)
        else:
            field_dict = self.field.get_along(*args, is_squeeze=is_squeeze)

        field = field_dict[symbol]

        return field

    # Inlined from Methods.Mesh.SolutionData.get_solution
    def get_solution(self, indice=None):
        """Return a copy of the solution with the option to only include specified indice.

        Parameters
        ----------
        self : SolutionData
            a SolutionData object
        indice : list
            list of indice, if list is empty or None all indice are included

        Returns
        -------
        solution: SolutionMat
            solution

        """
        logger = self.get_logger()

        # create copy to directly manipulate data
        solution = self.copy()

        if indice:
            axes = solution.field.axes
            axes_names = solution.get_axes_list()[0]
            ax_idx = axes_names.index("indice")

            org_indice = axes[ax_idx].get_values()

            if set(indice) - set(org_indice):
                logger.warning(
                    "At least one input indice is not part of the solution. "
                    + "Respective indice will be skipped."
                )

            # skip indice that are not part of the solution
            new_indice = [ii for ii in indice if ii in org_indice]

            # create requested axes list to get field values (see SciDataTool slicing ref.)
            args = [
                name + "[smallestperiod]" if name != "indice" else name
                for name in axes_names
            ]
            args[ax_idx] += "=axis_data"

            # get the field values
            field_dict = solution.field.get_along(
                *args, axis_data={"indice": new_indice}
            )

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
            solution.field.values = field_dict[self.field.symbol]

        return solution
