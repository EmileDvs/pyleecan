# Experimental dataclass generated from Generator/ClassesRef/Output/XOutput.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from ..definitions import config_dict
from ..Functions.init_fig import init_fig
from ..Functions.SciDataTool.Plot.plot_2D import plot_2D
from .data_keeper import DataKeeper
from .opti_objective import OptiObjective
from .output import Output
from .param_explorer import ParamExplorer


@dataclass(eq=False)
class XOutput(Output):
    """XOutput object: gather all the outputs of all the modules for multiple simulations

    Attributes
    ----------
    paramexplorer_list : [ParamExplorer] or None
        List containing ParamExplorer
        Default: None
    output_list : [Output] or None
        List containing Output (or Xoutput) for each simulation
        Default: None
    xoutput_dict : {DataKeeper} or None
        dictionary containing DataKeeper
        Default: None
    nb_simu : int
        Number of simulations excluding reference simulation
        Default: 0; Minimum: 0
    xoutput_ref : Output or None
        Xoutput (or Output) of the reference simulation (only if is_keep_all_output is True and not included in output_list)
        Default: None
    xoutput_ref_index : int or None
        Index of the Xoutput (or Output) of the reference simulation in the output_list (only if is_keep_all_output is True)
        Default: None
    """

    COLORS = config_dict["PLOT"]["COLOR_DICT"]["COLOR_LIST"]
    COLORMAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]
    FONT_NAME = config_dict["PLOT"]["FONT_NAME"]
    FONT_SIZE_TITLE = config_dict["PLOT"]["FONT_SIZE_TITLE"]
    FONT_SIZE_LABEL = config_dict["PLOT"]["FONT_SIZE_LABEL"]
    FONT_SIZE_LEGEND = config_dict["PLOT"]["FONT_SIZE_LEGEND"]
    paramexplorer_list: list[ParamExplorer] | None = None
    """List containing ParamExplorer"""
    output_list: list[Output] | None = None
    """List containing Output (or Xoutput) for each simulation"""
    xoutput_dict: dict[str, DataKeeper] | None = None
    """dictionary containing DataKeeper"""
    nb_simu: int = 0
    """Number of simulations excluding reference simulation"""
    xoutput_ref: Output | None = None
    """Xoutput (or Output) of the reference simulation (only if is_keep_all_output is True and not included in output_list)"""
    xoutput_ref_index: int | None = None
    """Index of the Xoutput (or Output) of the reference simulation in the output_list (only if is_keep_all_output is True)"""

    # Inlined from Methods.Output.XOutput.__delitem__
    def __delitem__(self, key):
        """Called to implement deletion of self[key]."""
        return self.xoutput_dict.__delitem__(key)

    def _get_symbol_data_(self, symbol, index):
        """Helper function to get data and label by symbol to avoid duplicate code."""
        if symbol in self.keys():
            data = self[symbol]
            values = np.array(data.result)[index]
        elif symbol in [pe.symbol for pe in self.paramexplorer_list]:
            data = self.get_paramexplorer(symbol)
            values = np.array(data.value)[index]
        else:
            symbol_ = next(iter(self.keys()))
            self.get_logger().warning(
                f"XOutput.plot_pareto(): Symbol '{symbol}' not found. "
                + f"Using symbol '{symbol_}' instead."
            )
            symbol = symbol_
            data = self[symbol]
            values = np.array(data.result)[index]
        label = symbol
        if data.unit not in ["", None]:
            label += " [{}]".format(data.unit)
        return (values, label)

    # Inlined from Methods.Output.XOutput.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a list or a dict and iterate in the object"""
        if isinstance(idx, int) or isinstance(idx, slice):
            return self.output_list.__getitem__(idx)
        else:
            return self.xoutput_dict.__getitem__(idx)

    # Inlined from Methods.Output.XOutput.__iter__
    def __iter__(self):
        """Method to behave like a list and iterate in the object"""
        return iter(self.output_list)

    # Inlined from Methods.Output.XOutput.__len__
    def __len__(self):
        """Method to behave like a list and iterate in the object"""
        if self.nb_simu != None:
            return self.nb_simu
        else:
            return len(self.output_list)

    # Inlined from Methods.Output.XOutput.__missing__
    def __missing__(self, key):
        """
        Called by XOutput.__getitem__() to implement self[key]
        for dict subclasses when key is not in the dictionary.
        """
        return self.xoutput_dict.__missing__(key)

    # Inlined from Methods.Output.XOutput.__next__
    def __next__(self):
        """Method to behave like a list and iterate in the object"""
        return next(self.output_list)

    # Inlined from Methods.Output.XOutput.__reversed__
    def __reversed__(self):
        """Built-in to implement reverse iteration"""
        return reversed(self.output_list)

    # Inlined from Methods.Output.XOutput.__setitem__
    def __setitem__(self, key, value):
        """Called to implement assignment to self[key]."""
        if isinstance(key, int) or isinstance(key, slice):
            return self.output_list.__setitem__(key, value)
        else:
            return self.xoutput_dict.__setitem__(key, value)

    # Inlined from Methods.Output.XOutput.append
    def append(self, elem):
        """Method to behave like a list and access quickly to output_list"""
        return self.output_list.append(elem)

    # Inlined from Methods.Output.XOutput.count
    def count(self, x):
        """
        Return the number of times x appears in the list.
        """

        return self.output_list.count(x)

    # Inlined from Methods.Output.XOutput.get_param_simu
    def get_param_simu(self, idx):
        """
        Return the list of parameter values for a specific simulation
        """
        assert len(idx) == len(self.shape)

        # Create a list to store values
        param_value = []
        for pe in self.paramexplorer_list:
            param_value.append(pe.value[idx])

        return param_value

    # Inlined from Methods.Output.XOutput.get_paramexplorer
    def get_paramexplorer(self, symbol):
        """Get the ParamExplorer with symbol
        Parameters
        ----------
        symbol: str
            ParamExplorer symbol
        """
        for paramexplorer in self.paramexplorer_list:
            if paramexplorer.symbol == symbol:
                return paramexplorer

        raise self.XOutputError("Unknown symbol {}".format(symbol))

    # Inlined from Methods.Output.XOutput.get_pareto_index
    def get_pareto_index(self):
        """Return index of individuals in the pareto

        Parameters
        ----------
        self: XOutput

        Returns
        -------
        idx_non_dom: list
            list of index of non dominated individuals
        """

        # Gather fitness results
        data = [
            val.result
            for _, val in self.xoutput_dict.items()
            if isinstance(val, OptiObjective)
        ]
        fitness = np.array(data).T

        # Get fitness values and ngen
        is_valid = np.array(self["is_valid"])

        # Keep only valid values
        indx = np.where(is_valid)
        fitness = fitness[indx]

        # Get pareto front
        pareto = fitness

        # Get dominated values
        idx_non_dom = list(range(len(pareto)))
        N = len(pareto)
        for i in range(N):
            for j in idx_non_dom:
                if all(pareto[j] <= pareto[i]) and any(pareto[j] < pareto[i]):
                    idx_non_dom.remove(i)
                    break

        return idx_non_dom

    # Inlined from Methods.Output.XOutput.get_simu
    def get_simu(self, index):
        """
        Generate a simulation according to index

        Parameters
        ----------
        index: int
            simulation index

        Returns
        -------
        simu : Simulation
            simulation generated
        """

        # Get reference simulation
        ref_simu = self.simu

        # Construct the simulation
        simu = ref_simu.copy()
        simu.var_simu = None

        # Run setters
        for paramexplorer in self.paramexplorer_list:
            paramexplorer.setter(simu, paramexplorer.value[index])

        return simu

    # Inlined from Methods.Output.XOutput.get_symbol_list
    def get_symbol_list(self):
        """
        Return the list of the symobl of the DataKeeper and ParamExplorer
        """
        symbol_list = list(self.keys())  # DataKeeper or OptiObjective
        symbol_list.extend([pe.symbol for pe in self.paramexplorer_list])

        return symbol_list

    # Inlined from Methods.Output.XOutput.get_xoutput_ref
    def get_xoutput_ref(self):
        """Return the reference XOutput (or Output) either from xoutput_ref or output_list

        Parameters
        ----------
        self : XOutput
            A XOutput object
        Returns
        -------
        xoutput_ref: XOutput
            reference XOutput (or Output) (if defined)
        """

        if self.xoutput_ref_index is not None:
            return self.output_list[self.xoutput_ref_index]
        else:
            return self.xoutput_ref

    # Inlined from Methods.Output.XOutput.insert
    def insert(self, i, x):
        """
        Insert an item at a given position.
        The first argument is the index of the element before which to insert,
        so a.insert(0, x) inserts at the front of the list, and a.insert(len(a), x) is equivalent to a.append(x).
        """
        return self.output_list.insert(i, x)

    # Inlined from Methods.Output.XOutput.items
    def items(self):
        """Returns self.xoutput_dict.items to behave like a dict"""

        return self.xoutput_dict.items()

    # Inlined from Methods.Output.XOutput.keys
    def keys(self):
        """Return xoutput_dict keys to behave like a dict"""
        if self.xoutput_dict is None:
            return []
        else:
            return self.xoutput_dict.keys()

    # Inlined from Methods.Output.XOutput.plot_generation
    def plot_generation(self, x_symbol, y_symbol, ax=None):
        """Plot every fitness values according to the two fitness

        Parameters
        ----------
        self : XOutput
        obj1 : str
            symbol of the ParamExplorer, the OptiObjective or the DataKeeper
        obj2 : str
            symbol of the ParamExplorer, the OptiObjective or the DataKeeper
        """

        # TODO define the colormap according to Pyleecan graphical chart
        # Colormap definition
        cm = LinearSegmentedColormap.from_list(
            "colormap",
            [(35 / 255, 89 / 255, 133 / 255), (250 / 255, 202 / 255, 56 / 255)],
            N=max(self["ngen"].result) + 1,
        )

        # Get fitness and ngen
        is_valid = np.array(self["is_valid"].result)
        ngen = np.array(self["ngen"].result)

        # Keep only valid values
        indx = np.where(is_valid)[0]

        ngen = ngen[indx]

        # get data and labels
        x_values, x_label = self._get_symbol_data_(self, x_symbol, indx)
        y_values, y_label = self._get_symbol_data_(self, y_symbol, indx)

        if ax is None:
            fig, ax = plt.subplots()

            # Plot fitness values
            scatter = ax.scatter(x_values, y_values, s=8, c=ngen, cmap=cm)

            # Add legend
            legend1 = ax.legend(
                *scatter.legend_elements(), loc="upper right", title="Generation"
            )
            ax.add_artist(legend1)

            # Extend xlim to give some space to the legend
            left, right = ax.get_xlim()
            ax.set_xlim(left, right + 0.2 * abs(right - left))

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title("Fitness values for each individual")
            fig.show()

        else:
            # Plot fitness values
            scatter = ax.scatter(x_values, y_values, s=8, c=ngen, cmap=cm)

            # Add legend
            legend1 = ax.legend(
                *scatter.legend_elements(), loc="upper right", title="Generation"
            )
            ax.add_artist(legend1)

            # Extend xlim to give some space to the legend
            left, right = ax.get_xlim()
            ax.set_xlim(left, right + 0.2 * abs(right - left))

            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title("Fitness values for each individual")

            return ax

    # Inlined from Methods.Output.XOutput.plot_multi
    def plot_multi(
        self,
        x_symbol,
        y_symbol,
        c_symbol=None,
        cmap=None,
        plot_type="point",
        idx=None,
        fig=None,
        ax=None,
        title=None,
        is_show_fig=True,
        save_path=None,
        win_title=None,
    ):
        """2D Plot from a DataKeeper / OptiObjective / ParamExplorer as a function of another
        DataKeeper / OptiObjective / ParamExplorer

        Parameters
        ----------
        self : XOutput
            XOutput object
        x_symbol: str
            ParamExplorer or DataKeeper symbol
        y_symbol: str
            ParamExplorer or DataKeeper symbol
        c_symbol: str
            optional symbol to set the plot colors
        cmap: colormap
            optional colormap
        plot_type: str
            scatter or plot to chose plot type
        idx: slice
            To plot only some data
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        title: str
            Figure or subfigure title according to ax
        is_show_fig : bool
            True to show figure after plot
        save_path : str
            full path of the png file where the figure is saved if save_path is not None
        win_title : str
            Title of the plot window

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot

        Raises
        ------
        PlotError
        """

        if idx is None:
            idx = slice(None)

        if plot_type not in ["point", "curve"]:
            raise self.PlotError(f"Unknown plot_type {plot_type}.")

        # get data and labels
        x_values, x_label = self._get_symbol_data_(self, x_symbol, idx)
        y_values, y_label = self._get_symbol_data_(self, y_symbol, idx)

        if c_symbol is None:
            colors = self.COLORS[0]
        else:
            # get the color data
            c_values, _ = self._get_symbol_data_(self, c_symbol, idx)
            colors = c_values[:, np.newaxis]

        # add legend
        if c_symbol is not None:
            legends = [c_symbol]
        else:
            legends = []

        if cmap is None:
            cmap = self.COLORMAP

        (fig, ax, _, _) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # call plot_2D function
        plot_2D(
            Xdatas=[x_values],
            Ydatas=[y_values],
            xlabel=x_label,
            ylabel=y_label,
            color_list=[colors],
            legend_list=legends,
            title=title,
            type_plot=plot_type,
            save_path=save_path,
            is_show_fig=is_show_fig,
            win_title=win_title,
            fig=fig,
            ax=ax,
            font_name=self.FONT_NAME,
            font_size_title=self.FONT_SIZE_TITLE,
            font_size_label=self.FONT_SIZE_LABEL,
            font_size_legend=self.FONT_SIZE_LEGEND,
        )
        return fig, ax

    # Inlined from Methods.Output.XOutput.plot_pareto
    def plot_pareto(
        self,
        x_symbol,
        y_symbol,
        c_symbol=None,
        cmap=None,
        ax=None,
        title=None,
        grid=False,
        is_show_fig=True,
        save_path=None,
    ):
        """Plot the pareto front for 2 objective functions

        Parameters
        ----------
        self : XOutput
        x_symbol : str
            symbol of the first objective function
        y_symbol: str
            symbol of the second objective function
        c_symbol: str
            optional symbol to set the plot colors
        cmap: colormap
            optional colormap
        is_show_fig : bool
            True to show figure after plot
        save_path : str
            full path of the png file where the figure is saved if save_path is not None
        """

        return self.parent.plot_pareto(
            x_symbol,
            y_symbol,
            c_symbol,
            cmap,
            ax,
            title,
            grid,
            is_show_fig,
            save_path,
        )

    # Inlined from Methods.Output.XOutput.pop
    def pop(self, i):
        """
        Remove the item at the given position in the list, and return it.
        If no index is specified, a.pop() removes and returns the last item in the list.
        """
        return self.list_output.pop(i)

    # Inlined from Methods.Output.XOutput.print_memory
    def print_memory(self, tab_level=0, detail_level=1, is_print=True):
        """Print an estimation of the memory usage for each property of the object

        Parameters
        ----------
        self : XOutput
            An XOutput object
        tab_level : int
            Number of tab ("    ") to add before each line
        detail_level : int
            Select how many data to display (0: only object size, 1: object + properties, 2:object + detailed properties)
        is_print: bool
            True print, else return str

        Returns
        -------
        mem_str: str
            if is_print == False, return the string that descibe the memory usage of the object
        """

        tab = ""
        for _ in range(tab_level):
            tab += "    "

        mem_str = tab + "Total XOutput size: " + str(getsizeof(self)) + " o\n"
        if detail_level == 0:
            print(mem_str)
            return

        mem_str += tab + "Reference simulation:\n"
        mem_str += super(type(self), self).print_memory(
            tab_level=tab_level + 1, detail_level=detail_level, is_print=False
        )

        mem_str += "\nXOutput Data:\n"
        # Paramexplorer_list
        S1 = 0
        if self.paramexplorer_list is not None:
            for obj in self.paramexplorer_list:
                S1 += getsizeof(obj)
        mem_str += tab + "    paramexplorer_list: " + str(S1) + " o\n"
        # output_list
        S2 = 0
        out_list_str = ""
        if self.output_list is not None:
            for ii, obj in enumerate(self.output_list):
                S = getsizeof(obj)
                S2 += S
                out_list_str += (
                    tab + "        output_list[" + str(ii) + "]: " + str(S) + " o\n"
                )
                if detail_level > 2:
                    out_list_str += self.output_list[ii].print_memory(
                        tab_level=3, detail_level=detail_level - 2, is_print=False
                    )
        mem_str += tab + "    output_list: " + str(S2) + " o\n"
        mem_str += out_list_str
        # xoutput_dict
        S3 = 0
        if self.xoutput_dict is not None:
            for key, value in self.xoutput_dict.items():
                S3 += getsizeof(key) + getsizeof(value)
        mem_str += tab + "    xoutput_dict: " + str(S3) + " o\n"
        mem_str += tab + "    nb_simu: " + str(getsizeof(self.nb_simu)) + " o\n"

        if is_print:
            print(mem_str)
        else:
            return mem_str

    # Inlined from Methods.Output.XOutput.remove
    def remove(self, x):
        """
        Remove the first item from the list whose value is equal to x.
        It raises a ValueError if there is no such item.
        """
        return self.output_list.remove(x)

    class PlotError(Exception):
        pass

    class XOutputError(Exception):
        pass
