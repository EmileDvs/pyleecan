# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Output/XOutput.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Output/XOutput
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Output import Output

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.OptiObjective import OptiObjective
from matplotlib.colors import LinearSegmentedColormap
from pyleecan.definitions import config_dict
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.SciDataTool.Plot.plot_2D import plot_2D
from sys import getsizeof


from pyleecan.Classes._check import InitUnKnowClassError


class XOutput(Output):
    """XOutput object: gather all the outputs of all the modules for multiple simulations"""

    VERSION = 1
    COLORS = config_dict["PLOT"]["COLOR_DICT"]["COLOR_LIST"]
    COLORMAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]
    FONT_NAME = config_dict["PLOT"]["FONT_NAME"]
    FONT_SIZE_TITLE = config_dict["PLOT"]["FONT_SIZE_TITLE"]
    FONT_SIZE_LABEL = config_dict["PLOT"]["FONT_SIZE_LABEL"]
    FONT_SIZE_LEGEND = config_dict["PLOT"]["FONT_SIZE_LEGEND"]

    # cf Methods.Output.XOutput.__delitem__
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

    # cf Methods.Output.XOutput.__getitem__
    def __getitem__(self, idx):
        """Method to behave like a list or a dict and iterate in the object"""
        if isinstance(idx, int) or isinstance(idx, slice):
            return self.output_list.__getitem__(idx)
        else:
            return self.xoutput_dict.__getitem__(idx)

    # cf Methods.Output.XOutput.__iter__
    def __iter__(self):
        """Method to behave like a list and iterate in the object"""
        return iter(self.output_list)

    # cf Methods.Output.XOutput.__len__
    def __len__(self):
        """Method to behave like a list and iterate in the object"""
        if self.nb_simu != None:
            return self.nb_simu
        else:
            return len(self.output_list)

    # cf Methods.Output.XOutput.__missing__
    def __missing__(self, key):
        """
        Called by XOutput.__getitem__() to implement self[key]
        for dict subclasses when key is not in the dictionary.
        """
        return self.xoutput_dict.__missing__(key)

    # cf Methods.Output.XOutput.__next__
    def __next__(self):
        """Method to behave like a list and iterate in the object"""
        return next(self.output_list)

    # cf Methods.Output.XOutput.__reversed__
    def __reversed__(self):
        """Built-in to implement reverse iteration"""
        return reversed(self.output_list)

    # cf Methods.Output.XOutput.__setitem__
    def __setitem__(self, key, value):
        """Called to implement assignment to self[key]."""
        if isinstance(key, int) or isinstance(key, slice):
            return self.output_list.__setitem__(key, value)
        else:
            return self.xoutput_dict.__setitem__(key, value)

    # cf Methods.Output.XOutput.append
    def append(self, elem):
        """Method to behave like a list and access quickly to output_list"""
        return self.output_list.append(elem)

    # cf Methods.Output.XOutput.count
    def count(self, x):
        """
        Return the number of times x appears in the list.
        """

        return self.output_list.count(x)

    # cf Methods.Output.XOutput.get_param_simu
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

    # cf Methods.Output.XOutput.get_paramexplorer
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

        raise XOutputError("Unknown symbol {}".format(symbol))

    # cf Methods.Output.XOutput.get_pareto_index
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

    # cf Methods.Output.XOutput.get_simu
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

    # cf Methods.Output.XOutput.get_symbol_list
    def get_symbol_list(self):
        """
        Return the list of the symobl of the DataKeeper and ParamExplorer
        """
        symbol_list = list(self.keys())  # DataKeeper or OptiObjective
        symbol_list.extend([pe.symbol for pe in self.paramexplorer_list])

        return symbol_list

    # cf Methods.Output.XOutput.get_xoutput_ref
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

    # cf Methods.Output.XOutput.insert
    def insert(self, i, x):
        """
        Insert an item at a given position.
        The first argument is the index of the element before which to insert,
        so a.insert(0, x) inserts at the front of the list, and a.insert(len(a), x) is equivalent to a.append(x).
        """
        return self.output_list.insert(i, x)

    # cf Methods.Output.XOutput.items
    def items(self):
        """Returns self.xoutput_dict.items to behave like a dict"""

        return self.xoutput_dict.items()

    # cf Methods.Output.XOutput.keys
    def keys(self):
        """Return xoutput_dict keys to behave like a dict"""
        if self.xoutput_dict is None:
            return list()
        else:
            return self.xoutput_dict.keys()

    # cf Methods.Output.XOutput.plot_generation
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

    # cf Methods.Output.XOutput.plot_multi
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
            raise PlotError(f"Unknown plot_type {plot_type}.")

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

    # cf Methods.Output.XOutput.plot_pareto
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

    # cf Methods.Output.XOutput.pop
    def pop(self, i):
        """
        Remove the item at the given position in the list, and return it.
        If no index is specified, a.pop() removes and returns the last item in the list.
        """
        return self.list_output.pop(i)

    # cf Methods.Output.XOutput.print_memory
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

    # cf Methods.Output.XOutput.remove
    def remove(self, x):
        """
        Remove the first item from the list whose value is equal to x.
        It raises a ValueError if there is no such item.
        """
        return self.output_list.remove(x)

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        paramexplorer_list=-1,
        output_list=-1,
        xoutput_dict=-1,
        nb_simu=0,
        xoutput_ref=None,
        xoutput_ref_index=None,
        simu=-1,
        path_result="",
        geo=-1,
        elec=-1,
        mag=-1,
        struct=-1,
        post=-1,
        logger_name="Pyleecan.Output",
        force=-1,
        loss=-1,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "paramexplorer_list" in list(init_dict.keys()):
                paramexplorer_list = init_dict["paramexplorer_list"]
            if "output_list" in list(init_dict.keys()):
                output_list = init_dict["output_list"]
            if "xoutput_dict" in list(init_dict.keys()):
                xoutput_dict = init_dict["xoutput_dict"]
            if "nb_simu" in list(init_dict.keys()):
                nb_simu = init_dict["nb_simu"]
            if "xoutput_ref" in list(init_dict.keys()):
                xoutput_ref = init_dict["xoutput_ref"]
            if "xoutput_ref_index" in list(init_dict.keys()):
                xoutput_ref_index = init_dict["xoutput_ref_index"]
            if "simu" in list(init_dict.keys()):
                simu = init_dict["simu"]
            if "path_result" in list(init_dict.keys()):
                path_result = init_dict["path_result"]
            if "geo" in list(init_dict.keys()):
                geo = init_dict["geo"]
            if "elec" in list(init_dict.keys()):
                elec = init_dict["elec"]
            if "mag" in list(init_dict.keys()):
                mag = init_dict["mag"]
            if "struct" in list(init_dict.keys()):
                struct = init_dict["struct"]
            if "post" in list(init_dict.keys()):
                post = init_dict["post"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "force" in list(init_dict.keys()):
                force = init_dict["force"]
            if "loss" in list(init_dict.keys()):
                loss = init_dict["loss"]
        # Set the properties (value check and convertion are done in setter)
        self.paramexplorer_list = paramexplorer_list
        self.output_list = output_list
        self.xoutput_dict = xoutput_dict
        self.nb_simu = nb_simu
        self.xoutput_ref = xoutput_ref
        self.xoutput_ref_index = xoutput_ref_index
        # Call Output init
        super(XOutput, self).__init__(
            simu=simu,
            path_result=path_result,
            geo=geo,
            elec=elec,
            mag=mag,
            struct=struct,
            post=post,
            logger_name=logger_name,
            force=force,
            loss=loss,
        )
        # The class is frozen (in Output init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        XOutput_str = ""
        # Get the properties inherited from Output
        XOutput_str += super(XOutput, self).__str__()
        if len(self.paramexplorer_list) == 0:
            XOutput_str += "paramexplorer_list = []" + linesep
        for ii in range(len(self.paramexplorer_list)):
            tmp = (
                self.paramexplorer_list[ii].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            XOutput_str += (
                "paramexplorer_list[" + str(ii) + "] =" + tmp + linesep + linesep
            )
        if len(self.output_list) == 0:
            XOutput_str += "output_list = []" + linesep
        for ii in range(len(self.output_list)):
            tmp = (
                self.output_list[ii].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            XOutput_str += "output_list[" + str(ii) + "] =" + tmp + linesep + linesep
        if len(self.xoutput_dict) == 0:
            XOutput_str += "xoutput_dict = dict()" + linesep
        for key, obj in self.xoutput_dict.items():
            tmp = (
                self.xoutput_dict[key].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            XOutput_str += "xoutput_dict[" + key + "] =" + tmp + linesep + linesep
        XOutput_str += "nb_simu = " + str(self.nb_simu) + linesep
        if self.xoutput_ref is not None:
            tmp = (
                self.xoutput_ref.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            XOutput_str += "xoutput_ref = " + tmp
        else:
            XOutput_str += "xoutput_ref = None" + linesep + linesep
        XOutput_str += "xoutput_ref_index = " + str(self.xoutput_ref_index) + linesep
        return XOutput_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Output
        if not super(XOutput, self).__eq__(other):
            return False
        if other.paramexplorer_list != self.paramexplorer_list:
            return False
        if other.output_list != self.output_list:
            return False
        if other.xoutput_dict != self.xoutput_dict:
            return False
        if other.nb_simu != self.nb_simu:
            return False
        if other.xoutput_ref != self.xoutput_ref:
            return False
        if other.xoutput_ref_index != self.xoutput_ref_index:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Output
        diff_list.extend(
            super(XOutput, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other.paramexplorer_list is None and self.paramexplorer_list is not None
        ) or (other.paramexplorer_list is not None and self.paramexplorer_list is None):
            diff_list.append(name + ".paramexplorer_list None mismatch")
        elif self.paramexplorer_list is None:
            pass
        elif len(other.paramexplorer_list) != len(self.paramexplorer_list):
            diff_list.append("len(" + name + ".paramexplorer_list)")
        else:
            for ii in range(len(other.paramexplorer_list)):
                diff_list.extend(
                    self.paramexplorer_list[ii].compare(
                        other.paramexplorer_list[ii],
                        name=name + ".paramexplorer_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (other.output_list is None and self.output_list is not None) or (
            other.output_list is not None and self.output_list is None
        ):
            diff_list.append(name + ".output_list None mismatch")
        elif self.output_list is None:
            pass
        elif len(other.output_list) != len(self.output_list):
            diff_list.append("len(" + name + ".output_list)")
        else:
            for ii in range(len(other.output_list)):
                diff_list.extend(
                    self.output_list[ii].compare(
                        other.output_list[ii],
                        name=name + ".output_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if (other.xoutput_dict is None and self.xoutput_dict is not None) or (
            other.xoutput_dict is not None and self.xoutput_dict is None
        ):
            diff_list.append(name + ".xoutput_dict None mismatch")
        elif self.xoutput_dict is None:
            pass
        elif len(other.xoutput_dict) != len(self.xoutput_dict):
            diff_list.append("len(" + name + "xoutput_dict)")
        else:
            for key in self.xoutput_dict:
                diff_list.extend(
                    self.xoutput_dict[key].compare(
                        other.xoutput_dict[key],
                        name=name + ".xoutput_dict[" + str(key) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if other._nb_simu != self._nb_simu:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._nb_simu)
                    + ", other="
                    + str(other._nb_simu)
                    + ")"
                )
                diff_list.append(name + ".nb_simu" + val_str)
            else:
                diff_list.append(name + ".nb_simu")
        if (other.xoutput_ref is None and self.xoutput_ref is not None) or (
            other.xoutput_ref is not None and self.xoutput_ref is None
        ):
            diff_list.append(name + ".xoutput_ref None mismatch")
        elif self.xoutput_ref is not None:
            diff_list.extend(
                self.xoutput_ref.compare(
                    other.xoutput_ref,
                    name=name + ".xoutput_ref",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._xoutput_ref_index != self._xoutput_ref_index:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._xoutput_ref_index)
                    + ", other="
                    + str(other._xoutput_ref_index)
                    + ")"
                )
                diff_list.append(name + ".xoutput_ref_index" + val_str)
            else:
                diff_list.append(name + ".xoutput_ref_index")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Output
        S += super(XOutput, self).__sizeof__()
        if self.paramexplorer_list is not None:
            for value in self.paramexplorer_list:
                S += getsizeof(value)
        if self.output_list is not None:
            for value in self.output_list:
                S += getsizeof(value)
        if self.xoutput_dict is not None:
            for key, value in self.xoutput_dict.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.nb_simu)
        S += getsizeof(self.xoutput_ref)
        S += getsizeof(self.xoutput_ref_index)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from Output
        XOutput_dict = super(XOutput, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        if self.paramexplorer_list is None:
            XOutput_dict["paramexplorer_list"] = None
        else:
            XOutput_dict["paramexplorer_list"] = list()
            for obj in self.paramexplorer_list:
                if obj is not None:
                    XOutput_dict["paramexplorer_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs,
                        )
                    )
                else:
                    XOutput_dict["paramexplorer_list"].append(None)
        if self.output_list is None:
            XOutput_dict["output_list"] = None
        else:
            XOutput_dict["output_list"] = list()
            for obj in self.output_list:
                if obj is not None:
                    XOutput_dict["output_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs,
                        )
                    )
                else:
                    XOutput_dict["output_list"].append(None)
        if self.xoutput_dict is None:
            XOutput_dict["xoutput_dict"] = None
        else:
            XOutput_dict["xoutput_dict"] = dict()
            for key, obj in self.xoutput_dict.items():
                if obj is not None:
                    XOutput_dict["xoutput_dict"][key] = obj.as_dict(
                        type_handle_ndarray=type_handle_ndarray,
                        keep_function=keep_function,
                        **kwargs,
                    )
                else:
                    XOutput_dict["xoutput_dict"][key] = None
        XOutput_dict["nb_simu"] = self.nb_simu
        if self.xoutput_ref is None:
            XOutput_dict["xoutput_ref"] = None
        else:
            XOutput_dict["xoutput_ref"] = self.xoutput_ref.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        XOutput_dict["xoutput_ref_index"] = self.xoutput_ref_index
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        XOutput_dict["__class__"] = "XOutput"
        return XOutput_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.paramexplorer_list is None:
            paramexplorer_list_val = None
        else:
            paramexplorer_list_val = list()
            for obj in self.paramexplorer_list:
                paramexplorer_list_val.append(obj.copy())
        if self.output_list is None:
            output_list_val = None
        else:
            output_list_val = list()
            for obj in self.output_list:
                output_list_val.append(obj.copy())
        if self.xoutput_dict is None:
            xoutput_dict_val = None
        else:
            xoutput_dict_val = dict()
            for key, obj in self.xoutput_dict.items():
                xoutput_dict_val[key] = obj.copy()
        nb_simu_val = self.nb_simu
        if self.xoutput_ref is None:
            xoutput_ref_val = None
        else:
            xoutput_ref_val = self.xoutput_ref.copy()
        xoutput_ref_index_val = self.xoutput_ref_index
        if self.simu is None:
            simu_val = None
        else:
            simu_val = self.simu.copy()
        path_result_val = self.path_result
        if self.geo is None:
            geo_val = None
        else:
            geo_val = self.geo.copy()
        if self.elec is None:
            elec_val = None
        else:
            elec_val = self.elec.copy()
        if self.mag is None:
            mag_val = None
        else:
            mag_val = self.mag.copy()
        if self.struct is None:
            struct_val = None
        else:
            struct_val = self.struct.copy()
        if self.post is None:
            post_val = None
        else:
            post_val = self.post.copy()
        logger_name_val = self.logger_name
        if self.force is None:
            force_val = None
        else:
            force_val = self.force.copy()
        if self.loss is None:
            loss_val = None
        else:
            loss_val = self.loss.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            paramexplorer_list=paramexplorer_list_val,
            output_list=output_list_val,
            xoutput_dict=xoutput_dict_val,
            nb_simu=nb_simu_val,
            xoutput_ref=xoutput_ref_val,
            xoutput_ref_index=xoutput_ref_index_val,
            simu=simu_val,
            path_result=path_result_val,
            geo=geo_val,
            elec=elec_val,
            mag=mag_val,
            struct=struct_val,
            post=post_val,
            logger_name=logger_name_val,
            force=force_val,
            loss=loss_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.paramexplorer_list = None
        self.output_list = None
        self.xoutput_dict = None
        self.nb_simu = None
        if self.xoutput_ref is not None:
            self.xoutput_ref._set_None()
        self.xoutput_ref_index = None
        # Set to None the properties inherited from Output
        super(XOutput, self)._set_None()

    def _get_paramexplorer_list(self):
        """getter of paramexplorer_list"""
        if self._paramexplorer_list is not None:
            for obj in self._paramexplorer_list:
                if obj is not None:
                    obj.parent = self
        return self._paramexplorer_list

    def _set_paramexplorer_list(self, value):
        """setter of paramexplorer_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "paramexplorer_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("paramexplorer_list", value, "[ParamExplorer]")
        self._paramexplorer_list = value

    paramexplorer_list = property(
        fget=_get_paramexplorer_list,
        fset=_set_paramexplorer_list,
        doc="""List containing ParamExplorer

        :Type: [ParamExplorer]
        """,
    )

    def _get_output_list(self):
        """getter of output_list"""
        if self._output_list is not None:
            for obj in self._output_list:
                if obj is not None:
                    obj.parent = self
        return self._output_list

    def _set_output_list(self, value):
        """setter of output_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "output_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("output_list", value, "[Output]")
        self._output_list = value

    output_list = property(
        fget=_get_output_list,
        fset=_set_output_list,
        doc="""List containing Output (or Xoutput) for each simulation

        :Type: [Output]
        """,
    )

    def _get_xoutput_dict(self):
        """getter of xoutput_dict"""
        if self._xoutput_dict is not None:
            for key, obj in self._xoutput_dict.items():
                if obj is not None:
                    obj.parent = self
        return self._xoutput_dict

    def _set_xoutput_dict(self, value):
        """setter of xoutput_dict"""
        if type(value) is dict:
            for key, obj in value.items():
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[key] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "xoutput_dict"
                    )
                    value[key] = class_obj(init_dict=obj)
        if type(value) is int and value == -1:
            value = dict()
        check_var("xoutput_dict", value, "{DataKeeper}")
        self._xoutput_dict = value

    xoutput_dict = property(
        fget=_get_xoutput_dict,
        fset=_set_xoutput_dict,
        doc="""dictionary containing DataKeeper

        :Type: {DataKeeper}
        """,
    )

    def _get_nb_simu(self):
        """getter of nb_simu"""
        return self._nb_simu

    def _set_nb_simu(self, value):
        """setter of nb_simu"""
        check_var("nb_simu", value, "int", Vmin=0)
        self._nb_simu = value

    nb_simu = property(
        fget=_get_nb_simu,
        fset=_set_nb_simu,
        doc="""Number of simulations excluding reference simulation

        :Type: int
        :min: 0
        """,
    )

    def _get_xoutput_ref(self):
        """getter of xoutput_ref"""
        return self._xoutput_ref

    def _set_xoutput_ref(self, value):
        """setter of xoutput_ref"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "xoutput_ref"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Output = import_class("pyleecan.Classes", "Output", "xoutput_ref")
            value = Output()
        check_var("xoutput_ref", value, "Output")
        self._xoutput_ref = value

        if self._xoutput_ref is not None:
            self._xoutput_ref.parent = self

    xoutput_ref = property(
        fget=_get_xoutput_ref,
        fset=_set_xoutput_ref,
        doc="""Xoutput (or Output) of the reference simulation (only if is_keep_all_output is True and not included in output_list)

        :Type: Output
        """,
    )

    def _get_xoutput_ref_index(self):
        """getter of xoutput_ref_index"""
        return self._xoutput_ref_index

    def _set_xoutput_ref_index(self, value):
        """setter of xoutput_ref_index"""
        check_var("xoutput_ref_index", value, "int")
        self._xoutput_ref_index = value

    xoutput_ref_index = property(
        fget=_get_xoutput_ref_index,
        fset=_set_xoutput_ref_index,
        doc="""Index of the Xoutput (or Output) of the reference simulation in the output_list (only if is_keep_all_output is True)

        :Type: int
        """,
    )

    class XOutputError(Exception):
        pass

    class PlotError(Exception):
        pass


XOutputError = XOutput.XOutputError

PlotError = XOutput.PlotError
