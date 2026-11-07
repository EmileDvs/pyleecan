# Experimental dataclass generated from Generator/ClassesRef/Post/PostPlot.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass, field
from inspect import signature
from typing import Any

from ..Functions.Plot import dict_2D, dict_3D
from .post_method import PostMethod


@dataclass(eq=False)
class PostPlot(PostMethod):
    """Post-processing to do a plot which is a method of Output or other class if attribute is not None

    Attributes
    ----------
    method : str or None
        Name of the plot method to call (e.g. plot_2D_Data, plot_contour, plot_multi)
        Default: None
    name : str
        Name of the plot to use when saving the figure after plotting
        Default: "[]"
    param_list : list
        dictionary of parameters to pass to the plot method when executing it
        Default: []
    param_dict : dict
        dictionary of parameters to pass to the plot method when executing it
        Default: -1
    save_format : str
        File format extension ("png", "svg", "eps") in which to save the figure. The PostPlot automatically saves the figure in the results folder. The user can specify a different folder by specifying "save_path"=path_str or not save the figure by specifying "save_path"=None in param_dict, if the plot_method enables it.
        Default: "png"
    quantity : str or None
        Full path to the quantity to which apply the plot_method except Output (e.g. mag.B, elec.get_Is, mag.meshsolution)
        Default: None
    """

    method: str | None = None
    """Name of the plot method to call (e.g. plot_2D_Data, plot_contour, plot_multi)"""
    name: str = "[]"
    """Name of the plot to use when saving the figure after plotting"""
    param_list: list[Any] = field(default_factory=list)
    """dictionary of parameters to pass to the plot method when executing it"""
    param_dict: dict[str, Any] = field(default_factory=dict)
    """dictionary of parameters to pass to the plot method when executing it"""
    save_format: str = "png"
    """File format extension ("png", "svg", "eps") in which to save the figure. The PostPlot automatically saves the figure in the results folder. The user can specify a different folder by specifying "save_path"=path_str or not save the figure by specifying "save_path"=None in param_dict, if the plot_method enables it."""
    quantity: str | None = None
    """Full path to the quantity to which apply the plot_method except Output (e.g. mag.B, elec.get_Is, mag.meshsolution)"""

    # Inlined from Methods.Post.PostPlot.run
    def run(self, output):
        """Execute the plot contained in the PostPlot object and save it to save_path

        Parameters
        ----------
        self : PostPlot
            A PostPlot object
        output : Output
            an Output object

        """

        output.get_logger().info("Running Post-processing: " + self.name)
        try:
            if self.quantity is not None:
                obj = output.get_data_from_str(self.quantity)
            else:
                obj = output

            # Get plot method
            plot_method = getattr(obj, self.method)

            # Path to save the figure if save_path is not already in param_dict and is an argument of the plot method
            if "save_path" not in self.param_dict and "save_path" in str(
                signature(plot_method)
            ):
                # Get path of results folder in the Output
                result_path = output.get_path_result()

                # Check in case format begins with a "."
                if self.save_format[0] == ".":
                    str_format = self.save_format
                else:
                    str_format = "." + self.save_format

                # Build save_path of the picture
                self.param_dict["save_path"] = os.path.join(
                    result_path, self.name + str_format
                )
            # Disabling the display of the figure when plotting
            if "is_show_fig" not in self.param_dict:
                self.param_dict["is_show_fig"] = False
            # Add window title
            self.param_dict["win_title"] = self.name
            # Adding colors and fonts
            if self.method == "plot_2D_Data":
                self.param_dict = dict(self.param_dict, **dict_2D)
                self.param_dict["fund_harm_dict"] = output.get_fund_harm(obj)
            elif self.method == "plot_3D_Data":
                self.param_dict = dict(self.param_dict, **dict_3D)

            # Execute plot method
            plot_method(
                *self.param_list,
                **self.param_dict,
            )

        except Exception as e:
            output.get_logger().error(
                "Error while running Post-processing: " + self.name + "\n" + str(e)
            )
