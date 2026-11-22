# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Data.csv
"""Generated experimental dataclass; do not edit by hand."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from glob import glob
from typing import TYPE_CHECKING, ClassVar

import imageio
import numpy as np
from matplotlib.pyplot import subplots

from ...classes_common.check import check_var
from .._import import import_class
from .._legacy_class import LegacyClass
from .normalization import Normalization

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(eq=False)
class Data(LegacyClass):
    """Abstract class for all kinds of data

    Attributes
    ----------
    symbol : str
        Symbol of the variable (in latex syntax)
        Default: ""
    name : str
        Name of the physical quantity (to be used in plots)
        Default: ""
    unit : str
        Unit of the physical quantity (to be used in plots)
        Default: ""
    normalizations : {Normalization}
        Normalizations available for the field and its axes
        Default: {}
    """

    symbol: str = ""
    """Symbol of the variable (in latex syntax)"""
    name: str = ""
    """Name of the physical quantity (to be used in plots)"""
    unit: str = ""
    """Unit of the physical quantity (to be used in plots)"""
    normalizations: dict[str, Normalization] = field(default_factory=dict)
    """Normalizations available for the field and its axes"""

    _custom_setters: ClassVar[tuple[str, ...]] = ("normalizations",)
    """Fields set by a legacy custom setter (_set_<field>)"""
    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Data._set_normalizations
    def _set_normalizations(self, value) -> None:
        """setter of normalizations"""
        if type(value) is dict:
            for key, obj in value.items():
                if type(obj) is dict:
                    class_obj = import_class(obj.get("__class__"), "normalizations")
                    value[key] = class_obj.from_dict(obj)
                elif isinstance(
                    obj, (float, int, np.int32, np.int64, np.float32, np.float64)
                ):
                    # Local import: avoids circular imports
                    from .norm_ref import NormRef

                    value[key] = NormRef(ref=obj)
                elif isinstance(obj, (np.ndarray, list)):
                    # Local import: avoids circular imports
                    from .norm_vector import NormVector

                    value[key] = NormVector(vector=np.asarray(obj))
        if type(value) is int and value == -1:
            value = {}
        check_var("normalizations", value, "{Normalization}")
        self.normalizations = value

    # Inlined from Methods.SciDataTool.Data.animate_as_gif
    @staticmethod
    def animate_as_gif(
        func: Callable,
        data_list: Data | list[Data],
        save_path: str = "./",
        file_name: str = "animated_plot.gif",
        index_var: str = "t_index",
        index_max: int = 50,
        index_step: int = 1,
        component_list: list | None = None,
        **kwargs,
    ) -> None:
        """Animate an existing plot command as a gif: animate

        Parameters
        ----------
        func : function
            plot command
        data_list : Data or [Data]
            Data object or list to plot
        save_path : str
            path where to save the gif
        file_name : str
            name of the gif file
        index_var : str
            name of the plot parameter along which to animate
        index_max : int
            maximum value of the index
        index_step : int
            step for the index (number of frames = index_max / index_step)
        component_list : list
            list of component names to plot in separate figures
        kwargs : dict
            parameters of func
        """

        # Local import: circular import with the class module
        from .vector_field import VectorField

        with imageio.get_writer(os.path.join(save_path, file_name), mode="I") as writer:
            if isinstance(data_list, list):
                for i, data in enumerate(data_list):
                    if isinstance(data, VectorField):
                        if component_list is None:  # default: extract all components
                            component_list = data.components.keys()
                        ncomp = len(component_list)
                        fig, axs = subplots(
                            2, ncomp, tight_layout=True, figsize=(20, 10)
                        )
                        for j in range(0, index_max, index_step):
                            save_path_temp = save_path + "\\temp_" + str(j) + ".png"
                            kwargs["save_path"] = save_path_temp
                            for k, comp in enumerate(component_list):
                                func(
                                    data.components[comp],
                                    fig=fig,
                                    subplot_index=k,
                                    **kwargs,
                                )
                            image = imageio.imread(save_path_temp)
                            writer.append_data(image)

                    else:
                        for j in range(0, index_max, index_step):
                            save_path_temp = save_path + "\\temp_" + str(j) + ".png"
                            kwargs["save_path"] = save_path_temp
                            func(data, **kwargs)
                            image = imageio.imread(save_path_temp)
                            writer.append_data(image)

            else:
                if isinstance(data_list, VectorField):
                    if component_list is None:  # default: extract all components
                        component_list = data_list.components.keys()
                    ncomp = len(component_list)
                    for j in range(0, index_max, index_step):
                        fig, axs = subplots(
                            1, ncomp, tight_layout=True, figsize=(20, 10)
                        )
                        save_path_temp = save_path + "\\temp_" + str(j) + ".png"
                        kwargs[index_var] = j
                        kwargs["save_path"] = save_path_temp
                        for k, comp in enumerate(component_list):
                            func(
                                data_list.components[comp],
                                fig=fig,
                                subplot_index=k,
                                **kwargs,
                            )
                        image = imageio.imread(save_path_temp)
                        writer.append_data(image)
                else:
                    for j in range(0, index_max, index_step):
                        save_path_temp = save_path + "\\temp_" + str(j) + ".png"
                        kwargs[index_var] = j
                        kwargs["save_path"] = save_path_temp
                        func(data_list, **kwargs)
                        image = imageio.imread(save_path_temp)
                        writer.append_data(image)

        for file in glob(save_path + "\\temp_*"):
            os.remove(file)
