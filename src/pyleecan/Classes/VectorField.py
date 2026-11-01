# File generated according to Generator/ClassesRef/SciDataTool/VectorField.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/VectorField"""

from copy import copy
from os import linesep
from sys import getsizeof

import imageio
import matplotlib.pyplot as plt
import numpy as np

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.SciDataTool import AxisError
from pyleecan.Functions.SciDataTool.Plot import REV_COMP_DICT
from pyleecan.Functions.SciDataTool.Plot.init_fig import copy_fig, init_fig
from pyleecan.Functions.SciDataTool.Plot.plot_2D import plot_2D
from pyleecan.Functions.SciDataTool.conversions import (
    cart2pol,
    pol2cart,
    rphiz_to_xyz,
    rphiz_to_xyz_field,
    xyz_to_rphiz,
)
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class VectorField(FrozenClass):
    """Class for 2D or 3D vector fields (time or frequency domain)"""

    VERSION = 1

    # cf Methods.SciDataTool.VectorField.change_periodicity
    def change_periodicity(
        self, per_a_new, per_t_new, is_aper_a_new=None, is_aper_t_new=False
    ):
        """Change (anti-)periodicities of vectorfield given input periodicities before changing referential

        Parameters
        ----------
        self : VectorField
            A VectorField object
        per_a_new : int
            New number of space periodicities of the machine over 2*pi
        per_t_new : int
            New number of time periodicities of the machine over time period (p/felec by default if Nrev is None) in static or rotating referential
        is_aper_a_new : bool
            True if spatial anti-periodicity in requested for new vectorfield
        is_aper_t_new : bool
            True if time anti-periodicity in requested for new vectorfield

        Returns
        -------
        vf_new : VectorField
            Vectorfield converted with new periodicities
        """

        DataLinspace = import_class("pyleecan.Classes", "DataLinspace")
        DataPattern = import_class("pyleecan.Classes", "DataPattern")

        # Get axes list in original VectorField
        # Assumes axes are the following: time, angle, z and z is DataPattern or radius
        axes_list = self.get_axes()

        # Get replicating number for time axis
        per_t, is_aper_t = axes_list[0].get_periodicity()
        per_t = int(per_t / 2) if is_aper_t else per_t
        Nrep_t = int(per_t / per_t_new)
        Nt = Nrep_t * axes_list[0].get_length(
            is_oneperiod=Nrep_t > 1 or (Nrep_t == 1 and not is_aper_t_new),
            is_antiperiod=Nrep_t == 1 and is_aper_t_new,
        )

        # Get replicating number for angle axis
        per_a, is_aper_a = axes_list[1].get_periodicity()
        if is_aper_a_new is None:
            is_aper_a_new = is_aper_a
        per_a = int(per_a / 2) if is_aper_a else per_a
        Nrep_a = int(per_a / per_a_new)
        Na = Nrep_a * axes_list[1].get_length(
            is_oneperiod=Nrep_a > 1 or (Nrep_a == 1 and not is_aper_a_new),
            is_antiperiod=Nrep_a == 1 and is_aper_a_new,
        )

        if Nrep_t == 1 and Nrep_a == 1:
            # Return VectorField as it is
            return self.copy()

        # Init periodicity changed VectorField
        vf_new = type(self)(name=self.name, symbol=self.symbol, components=dict())

        # Keep time anti-periodicity if it exists
        if Nrep_t == 1 and is_aper_t_new:
            time_arg = "time[smallestperiod]"
        else:
            time_arg = "time[oneperiod]"

        # Keep spatial anti-periodicity if it exists
        if Nrep_a == 1 and is_aper_a_new:
            angle_arg = "angle[smallestperiod]"
        else:
            angle_arg = "angle[oneperiod]"

        # Get argument list for call to get_rphiz_along on one time and space period
        arg_list = [time_arg, angle_arg]
        if isinstance(self.get_axes()[-1], DataPattern):
            arg_list.append("z[smallestpattern]")
        else:
            arg_list.append(self.get_axes()[-1].name)

        # Get axes values on requested axes
        result = self.get_rphiz_along(*arg_list, is_squeeze=False)
        axes_list_new = list()
        for axis in axes_list:
            axis_new = axis.copy()
            # Change time periodicity
            if Nrep_t > 1 and axis.name == "time":
                axis_new.symmetries = {"period": per_t_new}
                time_full = result["time"]
                if isinstance(axis_new, DataLinspace):
                    if axis.include_endpoint:
                        t_final = time_full[-1] + time_full[1] - time_full[0]
                    else:
                        t_final = axis.final
                    axis_new.number = Nt
                    axis_new.final = Nrep_t * t_final
                    axis_new.include_endpoint = False
                else:
                    t_final = time_full[-1] + time_full[1] - time_full[0]
                    for k in range(1, Nrep_t):
                        time_full = np.append(time_full, result["time"] + k * t_final)
                    axis_new.values = time_full
            # Change angle periodicity
            if Nrep_a > 1 and axis.name == "angle":
                axis_new.symmetries = {"period": per_a_new}
                angle_full = result["angle"]
                if isinstance(axis_new, DataLinspace):
                    if axis.include_endpoint:
                        a_final = angle_full[-1] + angle_full[1] - angle_full[0]
                    else:
                        a_final = axis.final
                    axis_new.number = Na
                    axis_new.final = Nrep_a * a_final
                    axis_new.include_endpoint = False
                else:
                    a_final = angle_full[-1] + angle_full[1] - angle_full[0]
                    for k in range(1, Nrep_a):
                        angle_full = np.append(
                            angle_full, result["angle"] + k * a_final
                        )
                    axis_new.values = angle_full

            axes_list_new.append(axis_new)

        # Replicate values by the number of repetitions
        for comp, data in self.components.items():
            # Duplicate values
            if Nrep_t > 1 and Nrep_a > 1:
                val_new = np.tile(result[comp], (Nrep_t, Nrep_a, 1))
            elif Nrep_t > 1:
                val_new = np.tile(result[comp], (Nrep_t, 1, 1))
            elif Nrep_a > 1:
                val_new = np.tile(result[comp], (1, Nrep_a, 1))

            # Create new data object with updated periodicities
            data_new = type(data)(
                name=data.name,
                symbol=data.symbol,
                unit=data.unit,
                axes=axes_list_new,
                values=val_new,
                normalizations=data.normalizations.copy(),
                is_real=data.is_real,
            )

            # Store reduced periodicity data in VectorField
            vf_new.components[comp] = data_new

        return vf_new

    # cf Methods.SciDataTool.VectorField.change_referential
    def change_referential(
        self, rotation_speed, is_waveform, atol=1e-9, sym_t_new=dict(), atol_freq=1e-6
    ):
        """Change referential of vectorfield given input rotation speed (algebric to include rotation direction)

        Parameters
        ----------
        self : VectorField
            A VectorField object
        rotation_speed : float
            rotation speed [rpm]
        is_waveform: bool
            True to perform referential change in waveform domain (time/space) otherwise perform it in spectral domain (freqs/wavenumber)
        atol: float
            Absolute tolerance under which amplitudes are assumed to be 0
        sym_t_new: dict
            Dict of symmetries in new referential
        atol_freq: float
            Absolute tolerance under which frequencies are assumed to be equal

        Returns
        -------
        vf_new : VectorField
            Vectorfield converted in new referential
        """

        # Init referential changed VectorField
        vf_new = type(self)(name=self.name, symbol=self.symbol, components=dict())

        # Loop on components to convert them to new referential
        axes_list_change = list()
        arg_list = list()
        freqs_new = np.array([])
        I1 = np.array([])
        Irf_un = np.array([])
        Imask = np.array([])
        ta_in = tuple()
        ta_out = tuple()
        for comp, data in self.components.items():

            # Change referential
            (
                data_new,
                axes_list_change,
                arg_list,
                freqs_new,
                I1,
                Irf_un,
                ta_in,
                ta_out,
            ) = data.change_referential(
                rotation_speed,
                is_waveform,
                atol=0,
                axes_list_change=axes_list_change,
                arg_list=arg_list,
                freqs_new=freqs_new,
                I1=I1,
                Irf_un=Irf_un,
                sym_t_new=sym_t_new,
                ta_in=ta_in,
                ta_out=ta_out,
                atol_freq=atol_freq,
            )

            # Filter harmonics that are below input absolute tolerance
            if atol > 0 and not is_waveform:

                # Copy axis not to change axis in axes_list_change
                data_new.axes = [axis.copy() for axis in data_new.axes]

                # Filter harmonics that are below input absolute tolerance
                if Imask.size == 0:
                    val = np.abs(data_new.values)
                    val_max = np.max(val)
                    while val.ndim > 1:
                        val = np.sum(val, axis=-1)
                    Imask = val > val_max * atol
                data_new.axes[0].values = data_new.axes[0].values[Imask]
                data_new.values = data_new.values[Imask, ...]

            # Store referential changed data in VectorField
            vf_new.components[comp] = data_new

        return vf_new

    # cf Methods.SciDataTool.VectorField.filter_spectral_leakage
    def filter_spectral_leakage(self, freqs_th):
        """Filter spectral leakage from a SciDataTool VectorField object

        Parameters
        ----------
        self : VectorField
            a VectorField object to be filtered
        freqs_th : ndarray
            theoretical frequencies

        Returns
        -------
        vf_filt : VectorField
            Filtered vectorfield

        """

        # Init filtered VectorField
        vf_filt = type(self)(name=self.name, symbol=self.symbol, components=dict())

        axes_list = list()
        arg_list = list()
        Wmatf = np.array([])
        If = np.array([])
        for comp, data in self.components.items():
            # Filter components by components
            (
                data_filt,
                axes_list,
                arg_list,
                Wmatf,
                If,
                freqs_th,
            ) = data.filter_spectral_leakage(
                freqs_th, axes_list, arg_list, Wmatf, If, is_return_calc_data=True
            )
            # Store filtered data in VectorField
            vf_filt.components[comp] = data_filt

        return vf_filt

    # cf Methods.SciDataTool.VectorField.freq_to_time
    def freq_to_time(self):
        """Performs the Fourier Transform and stores the resulting field in a VectorField of DataTime objects.
        Parameters
        ----------
        self : VectorField
            a VectorField object
        Returns
        -------
        a VectorField object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
        VectorField = module.VectorField

        comp_dict = dict()
        for key, comp in self.components.items():
            comp_dict[key] = comp.freq_to_time()

        return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    # cf Methods.SciDataTool.VectorField.get_axes
    def get_axes(self, *args):
        """Returns the list of axes.
        Parameters
        ----------
        self: Data
            a Data object
        args : list
            list of axes names
        Returns
        -------
        axes_list : list of axes (Data)
        """

        axes = self.components[list(self.components.keys())[0]].axes

        if len(args) > 0:
            axes_list = []
            for name in args:
                for axis in axes:
                    if axis.name == name:
                        axes_list.append(axis)
        else:
            axes_list = axes

        return axes_list

    # cf Methods.SciDataTool.VectorField.get_harm_rphiz_along
    def get_harm_rphiz_along(
        self, N_harm, *args, unit="SI", is_norm=False, axis_data=[]
    ):
        """Returns the list of the cylindrical (r,phi,z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if "comp_x" in self.components.keys() and "comp_y" in self.components.keys():
            # Extract first along whole "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != []:
                new_args[args.index(string[0])] = "angle"
            else:
                new_args.extend(["angle"])
            Datax = self.components["comp_x"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            Datay = self.components["comp_y"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_x = Datax.values
            field_y = Datay.values
            shape = field_x.shape
            phi = Datax.get_axes("angle")[0].get_values()
            # Convert to cylindrical coordinates
            (field_r, field_t) = cart2pol(field_x, field_y, phi)
            # Extract second time with true args
            if "angle" not in args:
                Datax.values = field_r
                Datay.values = field_t
                self.components["radial"] = Datax
                self.components["tangential"] = Datay
                resultr = self.components["radial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_r = resultr[self.components["radial"].symbol]
                resultt = self.components["tangential"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_t = resultt[self.components["tangential"].symbol]
                # Delete temporary Data objects
                del self.components["radial"]
                del self.components["tangential"]
            else:
                # Need return dict to initialize results
                resultr = self.components["comp_x"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultr)
            del return_dict[self.components["comp_x"].symbol]

        elif "tangential" in self.components.keys():
            resultphi = self.components["tangential"].get_harmonics(
                N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_t = resultphi[self.components["tangential"].symbol]
            shape = field_t.shape
            if "radial" in self.components.keys():
                resultr = self.components["radial"].get_harmonics(
                    N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_r = resultphi[self.components["radial"].symbol]
            else:
                field_r = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_harmonics(
                    N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_harmonics(
                    N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultphi)
            del return_dict[self.components["tangential"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_harmonics(
                N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_t = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["z"].get_harmonics(
                N_harm, args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_t = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, comp_x, comp_y or comp_z"
            )

        return_dict["radial"] = field_r
        return_dict["tangential"] = field_t
        return_dict["axial"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.get_harm_xyz_along
    def get_harm_xyz_along(self, N_harm, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the list of the cartesian (x,y,z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if (
            "radial" in self.components.keys()
            and "tangential" in self.components.keys()
        ):
            # Extract first along whole "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != []:
                new_args[args.index(string[0])] = "angle"
            else:
                new_args.extend(["angle"])
            Datar = self.components["radial"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            Dataphi = self.components["tangential"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_r = Datar.values
            field_c = Dataphi.values
            shape = field_r.shape
            phi = Datar.get_axes("angle")[0].get_values()
            # Convert to cylindrical coordinates
            (field_x, field_y) = pol2cart(field_r, field_c, phi)
            # Extract second time with true args
            if "angle" not in args:
                Datar.values = field_x
                Dataphi.values = field_y
                self.components["comp_x"] = Datar
                self.components["comp_y"] = Dataphi
                resultx = self.components["comp_x"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_x = resultx[self.components["comp_x"].symbol]
                resulty = self.components["comp_y"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_y = resulty[self.components["comp_y"].symbol]
                # Delete temporary Data objects
                del self.components["comp_x"]
                del self.components["comp_y"]
            else:
                # Need return dict to initialize results
                resultx = self.components["radial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            # Build return dict
            return_dict = dict(resultx)
            del return_dict[self.components["radial"].symbol]

        elif "comp_x" in self.components.keys():
            resultx = self.components["comp_x"].get_harmonics(
                N_harm,
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_x = resultx[self.components["comp_x"].symbol]
            shape = field_x.shape
            if "comp_y" in self.components.keys():
                resulty = self.components["comp_y"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_y = resulty[self.components["comp_y"].symbol]
            else:
                field_y = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultx)
            del return_dict[self.components["comp_x"].symbol]

        elif "comp_y" in self.components.keys():
            resulty = self.components["comp_y"].get_harmonics(
                N_harm,
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_y = resulty[self.components["comp_y"].symbol]
            shape = field_y.shape
            if "comp_x" in self.components.keys():
                resultx = self.components["comp_x"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_x = resultx[self.components["comp_x"].symbol]
            else:
                field_x = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_harmonics(
                    N_harm,
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resulty)
            del return_dict[self.components["comp_y"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_harmonics(
                N_harm,
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["comp_z"].get_harmonics(
                N_harm,
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, comp_x, comp_y or comp_z"
            )

        return_dict["comp_x"] = field_x
        return_dict["comp_y"] = field_y
        return_dict["comp_z"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.get_mag_rphiz_along
    def get_mag_rphiz_along(self, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the list of the cylindrical (r,phi,z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if "comp_x" in self.components.keys() and "comp_y" in self.components.keys():
            # Extract first along whole "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != []:
                new_args[args.index(string[0])] = "angle"
            else:
                new_args.extend(["angle"])
            Datax = self.components["comp_x"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            Datay = self.components["comp_y"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_x = Datax.values
            field_y = Datay.values
            shape = field_x.shape
            phi = Datax.get_axes("angle")[0].get_values()
            # Convert to cylindrical coordinates
            (field_r, field_t) = cart2pol(field_x, field_y, phi)
            # Extract second time with true args
            if "angle" not in args:
                Datax.values = field_r
                Datay.values = field_t
                self.components["radial"] = Datax
                self.components["tangential"] = Datay
                resultr = self.components["radial"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_r = resultr[self.components["radial"].symbol]
                resultt = self.components["tangential"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_t = resultt[self.components["tangential"].symbol]
                # Delete temporary Data objects
                del self.components["radial"]
                del self.components["tangential"]
            else:
                # Need return dict to initialize results
                resultr = self.components["comp_x"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultr)
            del return_dict[self.components["comp_x"].symbol]

        elif "radial" in self.components.keys():
            resultr = self.components["radial"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_r = resultr[self.components["radial"].symbol]
            shape = field_r.shape
            if "tangential" in self.components.keys():
                resultphi = self.components["tangential"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_t = resultphi[self.components["tangential"].symbol]
            else:
                field_t = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultr)
            del return_dict[self.components["radial"].symbol]

        elif "tangential" in self.components.keys():
            resultphi = self.components["tangential"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_t = resultphi[self.components["tangential"].symbol]
            shape = field_t.shape
            if "radial" in self.components.keys():
                resultr = self.components["radial"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_r = resultphi[self.components["radial"].symbol]
            else:
                field_r = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultphi)
            del return_dict[self.components["tangential"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_t = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["comp_z"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_t = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, comp_x, comp_y or comp_z"
            )

        return_dict["radial"] = field_r
        return_dict["tangential"] = field_t
        return_dict["axial"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.get_mag_xyz_along
    def get_mag_xyz_along(self, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the list of the cartesian (comp_x,comp_y,comp_z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if (
            "radial" in self.components.keys()
            and "tangential" in self.components.keys()
        ):
            # Extract first along whole "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != []:
                new_args[args.index(string[0])] = "angle"
            else:
                new_args.extend(["angle"])
            Datar = self.components["radial"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            Dataphi = self.components["tangential"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_r = Datar.values
            field_c = Dataphi.values
            shape = field_r.shape
            phi = Datar.get_axes("angle")[0].get_values()
            # Convert to cylindrical coordinates
            (field_x, field_y) = pol2cart(field_r, field_c, phi)
            # Extract second time with true args
            if "angle" not in args:
                Datar.values = field_x
                Dataphi.values = field_y
                self.components["comp_x"] = Datar
                self.components["comp_y"] = Dataphi
                resultx = self.components["comp_x"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_x = resultx[self.components["comp_x"].symbol]
                resulty = self.components["comp_y"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_y = resulty[self.components["comp_y"].symbol]
                # Delete temporary Data objects
                del self.components["comp_x"]
                del self.components["comp_y"]
            else:
                # Need return dict to initialize results
                resultx = self.components["radial"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            # Build return dict
            return_dict = dict(resultx)
            del return_dict[self.components["radial"].symbol]

        elif "comp_x" in self.components.keys():
            resultx = self.components["comp_x"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_x = resultx[self.components["comp_x"].symbol]
            shape = field_x.shape
            if "comp_y" in self.components.keys():
                resulty = self.components["comp_y"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_y = resulty[self.components["comp_y"].symbol]
            else:
                field_y = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultx)
            del return_dict[self.components["comp_x"].symbol]

        elif "comp_y" in self.components.keys():
            resulty = self.components["comp_y"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_y = resulty[self.components["comp_y"].symbol]
            shape = field_y.shape
            if "comp_x" in self.components.keys():
                resultx = self.components["comp_x"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_x = resultx[self.components["comp_x"].symbol]
            else:
                field_x = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_magnitude_along(
                    args, unit=unit, is_norm=is_norm, axis_data=axis_data
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resulty)
            del return_dict[self.components["comp_y"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["comp_z"].get_magnitude_along(
                args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, comp_x, comp_y or comp_z"
            )

        return_dict["comp_x"] = field_x
        return_dict["comp_y"] = field_y
        return_dict["comp_z"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.get_rphiz_along
    def get_rphiz_along(
        self, *args, unit="SI", is_norm=False, axis_data=[], is_squeeze=True
    ):
        """Returns the list of the cylindrical (r,phi,z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if "comp_x" in self.components.keys() and "comp_y" in self.components.keys():
            # Extract first along whole or smallest period "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != [] and "smallestperiod" not in string[0]:
                new_args[args.index(string[0])] = "angle"
            elif string == []:
                if "wavenumber" in args:
                    new_args[args.index("wavenumber")] = "angle"
                else:
                    new_args.extend(["angle"])
            Datax = self.components["comp_x"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            Datay = self.components["comp_y"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_x = Datax.values
            field_y = Datay.values
            shape = field_x.shape
            if string != [] and "smallestperiod" in string[0]:
                phi = Datax.get_axes("angle")[0].get_values(is_smallestperiod=True)
            else:
                phi = Datax.get_axes("angle")[0].get_values()
            # Convert to cylindrical coordinates
            (field_r, field_c) = cart2pol(field_x, field_y, phi)
            # Extract second time with true args
            if "angle" not in args and "angle[smallestperiod]" not in args:
                Datax.values = field_r
                Datay.values = field_c
                self.components["radial"] = Datax
                self.components["tangential"] = Datay
                resultr = self.components["radial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_r = resultr[self.components["radial"].symbol]
                resultt = self.components["tangential"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_c = resultt[self.components["tangential"].symbol]
                # Delete temporary Data objects
                del self.components["radial"]
                del self.components["tangential"]
            else:
                # Need return dict to initialize results
                resultr = self.components["comp_x"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultr)
            del return_dict[self.components["comp_x"].symbol]

        elif "radial" in self.components.keys():
            resultr = self.components["radial"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_r = resultr[self.components["radial"].symbol]
            shape = field_r.shape
            if "tangential" in self.components.keys():
                resultphi = self.components["tangential"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_c = resultphi[self.components["tangential"].symbol]
            else:
                field_c = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultr)
            del return_dict[self.components["radial"].symbol]

        elif "tangential" in self.components.keys():
            resultphi = self.components["tangential"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_c = resultphi[self.components["tangential"].symbol]
            shape = field_c.shape
            if "radial" in self.components.keys():
                resultr = self.components["radial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_r = resultphi[self.components["radial"].symbol]
            else:
                field_r = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultphi)
            del return_dict[self.components["tangential"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_c = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["comp_z"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_r = np.zeros(shape)
            field_c = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, comp_x, comp_y or comp_z"
            )

        return_dict["radial"] = field_r
        return_dict["tangential"] = field_c
        return_dict["axial"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.get_vectorfield_along
    def get_vectorfield_along(self, *args, unit="SI", is_norm=False, axis_data=[]):
        """Returns the sliced or interpolated version of the data, using conversions and symmetries if needed.
        Parameters
        ----------
        self : VectorField
            a VectorField object
        Returns
        -------
        a VectorField object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
        VectorField = module.VectorField

        comp_dict = dict()

        for comp in self.components:  # Call get_data_along on each component
            comp_dict[comp] = self.components[comp].get_data_along(
                *args, unit=unit, is_norm=is_norm, axis_data=axis_data
            )

        return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    # cf Methods.SciDataTool.VectorField.get_xyz_along
    def get_xyz_along(
        self, *args, unit="SI", is_norm=False, axis_data=[], is_squeeze=True
    ):
        """Returns the list of the cartesian (comp_x,comp_y,comp_z) components of the field, using conversions and symmetries if needed.
        Parameters
        ----------
        self: Data
            a Data object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        unit: str
            Unit requested by the user ("SI" by default)
        is_norm: bool
            Boolean indicating if the field must be normalized (False by default)
        axis_data: list
            list of ndarray corresponding to user-input data
        Returns
        -------
        list of 1Darray of axes values, ndarray of field values
        """

        if len(args) == 1 and type(args[0]) == tuple:
            args = args[0]  # if called from another script with *args

        if "radial" in self.components.keys() or "tangential" in self.components.keys():
            # Extract first along whole or smallest period "angle" axis
            new_args = [arg for arg in args]
            string = [s for s in args if "angle" in s]
            if string != [] and "smallestperiod" not in string[0]:
                new_args[args.index(string[0])] = "angle"
            elif string == []:
                if "wavenumber" in args:
                    new_args[args.index("wavenumber")] = "angle[smallestperiod]"
                else:
                    new_args.extend(["angle[smallestperiod]"])
            Datar = self.components["radial"].get_data_along(
                *new_args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
            )
            field_r = Datar.values
            shape = field_r.shape
            if "tangential" in self.components.keys():
                Dataphi = self.components["tangential"].get_data_along(
                    *new_args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                )
                field_c = Dataphi.values
            else:
                field_c = np.zeros(shape, dtype=field_r.dtype)
                Dataphi = type(Datar)(
                    name=Datar.name,
                    unit=Datar.unit,
                    symbol=Datar.symbol,
                    axes=Datar.axes,
                    values=field_c,
                )
            phi = Datar.get_axes("angle")[0].get_values(is_smallestperiod=True)
            # Convert to cylindrical coordinates
            (field_x, field_y) = pol2cart(field_r, field_c, phi)
            # Extract second time with true args
            if "angle" not in args and "angle[smallestperiod]" not in args:
                Datar.values = field_x
                Dataphi.values = field_y
                self.components["comp_x"] = Datar
                self.components["comp_y"] = Dataphi
                resultx = self.components["comp_x"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_x = resultx[self.components["comp_x"].symbol]
                resulty = self.components["comp_y"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_y = resulty[self.components["comp_y"].symbol]
                # Delete temporary Data objects
                del self.components["comp_x"]
                del self.components["comp_y"]
            else:
                # Need return dict to initialize results
                resultx = self.components["radial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
            # Add axial component
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            # Build return dict
            return_dict = dict(resultx)
            del return_dict[self.components["radial"].symbol]

        elif "comp_x" in self.components.keys():
            resultx = self.components["comp_x"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_x = resultx[self.components["comp_x"].symbol]
            shape = field_x.shape
            if "comp_y" in self.components.keys():
                resulty = self.components["comp_y"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_y = resulty[self.components["comp_y"].symbol]
            else:
                field_y = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resultx)
            del return_dict[self.components["comp_x"].symbol]

        elif "comp_y" in self.components.keys():
            resulty = self.components["comp_y"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_y = resulty[self.components["comp_y"].symbol]
            shape = field_y.shape
            if "comp_x" in self.components.keys():
                resultx = self.components["comp_x"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_x = resultx[self.components["comp_x"].symbol]
            else:
                field_x = np.zeros(shape)
            if "axial" in self.components.keys():
                resultz = self.components["axial"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["axial"].symbol]
            elif "comp_z" in self.components.keys():
                resultz = self.components["comp_z"].get_along(
                    args,
                    unit=unit,
                    is_norm=is_norm,
                    axis_data=axis_data,
                    is_squeeze=is_squeeze,
                )
                field_z = resultz[self.components["comp_z"].symbol]
            else:
                field_z = np.zeros(shape)
            return_dict = dict(resulty)
            del return_dict[self.components["comp_y"].symbol]

        elif "axial" in self.components.keys():
            resultz = self.components["axial"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_z = resultz[self.components["axial"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = dict(resultz)
            del return_dict[self.components["axial"].symbol]

        elif "comp_z" in self.components.keys():
            resultz = self.components["comp_z"].get_along(
                args,
                unit=unit,
                is_norm=is_norm,
                axis_data=axis_data,
                is_squeeze=is_squeeze,
            )
            field_z = resultz[self.components["comp_z"].symbol]
            shape = field_z.shape
            field_x = np.zeros(shape)
            field_y = np.zeros(shape)
            return_dict = resultz
            del return_dict[self.components["comp_z"].symbol]

        else:
            raise AxisError(
                "Vector_field object is empty (should contain at least radial, tangential, axial, x, y or z"
            )

        return_dict["comp_x"] = field_x
        return_dict["comp_y"] = field_y
        return_dict["comp_z"] = field_z

        return return_dict

    # cf Methods.SciDataTool.VectorField.plot_2D_Data
    def plot_2D_Data(
        self,
        *arg_list,
        axis_data=None,
        radius=None,
        is_norm=False,
        unit="SI",
        component_list=None,
        data_list=[],
        legend_list=[],
        color_list=None,
        linestyles=None,
        linewidth_list=[1.5],
        save_path=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        is_logscale_x=False,
        is_logscale_y=False,
        is_disp_title=True,
        is_grid=True,
        is_auto_ticks=True,
        is_auto_range=False,
        fig=None,
        ax=None,
        barwidth=100,
        type_plot=None,
        fund_harm_dict=None,
        is_show_fig=None,
        win_title=None,
        thresh=None,
        font_name="arial",
        font_size_title=12,
        font_size_label=10,
        font_size_legend=8,
        scale_units="x",
        scale=None,
        width=0.005,
        phase=0,
        is_show_legend=True,
        is_outside_legend=False,
        is_frame_legend=True,
    ):
        """Plots a field as a function of time

        Parameters
        ----------
        self : Output
            an Output object
        Data_str : str
            name of the Data Object to plot (e.g. "mag.Br")
        *arg_list : list of str
            arguments to specify which axes to plot
        radius : float
            radius used for quiver plot
        is_norm : bool
            boolean indicating if the field must be normalized
        unit : str
            unit in which to plot the field
        data_list : list
            list of Data objects to compare
        component_list : list
            list of component names to plot in separate figures
        legend_list : list
            list of legends to use for each Data object (including reference one) instead of data.name
        color_list : list
            list of colors to use for each Data object
        save_path : str
            full path of the png file where the figure is saved if save_path is not None
        x_min : float
            minimum value for the x-axis
        x_max : float
            maximum value for the x-axis
        y_min : float
            minimum value for the y-axis
        y_max : float
            maximum value for the y-axis
        is_logscale_x : bool
            boolean indicating if the x-axis must be set in logarithmic scale
        is_logscale_y : bool
            boolean indicating if the y-axis must be set in logarithmic scale
        is_disp_title : bool
            boolean indicating if the title must be displayed
        is_grid : bool
            boolean indicating if the grid must be displayed
        is_auto_ticks : bool
            in fft, adjust ticks to freqs (deactivate if too close)
        is_auto_range : bool
            in fft, display up to 1% of max
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        barwidth : float
            barwidth scaling factor, only if type_plot = "bargraph"
        type_plot : str
            type of 2D graph : "curve", "bargraph", "barchart" or "quiver"
        fund_harm_dict : dict
            Dict containing axis name as key and frequency/order/wavenumber of fundamental harmonic as value to display fundamental harmonic in red in the fft
        is_show_fig : bool
            True to show figure after plot
        thresh : float
            threshold for automatic fft ticks
        scale_units : str
            arrow lenght scale factor reference {'width', 'height', 'dots', 'pouces', 'x', 'y', 'xy'}
        scale : float
            arrow length factor
        width : float
            arrow width factor
        is_outside_legend : bool
            True to display legend outside the graph
        is_frame_legend : bool
            True to display legend in a frame
        """

        # Dynamic import to avoid import loop
        DataPattern = import_class("pyleecan.Classes", "DataPattern")

        # Special case of quiver plot
        if type_plot == "quiver":
            if component_list is None:
                title = "Total " + self.name
                result = self.get_xyz_along(
                    arg_list,
                    axis_data=axis_data,
                    unit=unit,
                    is_norm=is_norm,
                )

                if "x" in result and "y" in result:
                    Xdatas = np.column_stack((result["x"], result["y"]))
                else:
                    if radius is None:
                        radius = 1
                    phi = result["angle"]
                    rphi = np.column_stack((np.array([radius] * len(phi)), phi))
                    Xdatas = rphiz_to_xyz(rphi)

                Ydatas = np.column_stack(
                    (np.squeeze(result["comp_x"]), np.squeeze(result["comp_y"]))
                )
            else:
                title = REV_COMP_DICT[component_list[0]].capitalize() + " " + self.name
                if component_list[0] in ["comp_x", "comp_y"]:
                    vecfield = self.to_xyz()
                    result = vecfield.components[component_list[0]].get_along(
                        arg_list,
                        axis_data=axis_data,
                        unit=unit,
                        is_norm=is_norm,
                    )
                    if "x" in result and "y" in result:
                        Xdatas = np.column_stack((result["x"], result["y"]))
                    else:
                        if radius is None:
                            radius = 1
                        phi = result["angle"]
                        rphi = np.column_stack((np.array([radius] * len(phi)), phi))
                        Xdatas = rphiz_to_xyz(rphi)
                    Y_comp = result[vecfield.components[component_list[0]].symbol]
                    if component_list[0] == "comp_x":
                        Y_comp[Xdatas[:, 0] < 0] = -Y_comp[Xdatas[:, 0] < 0]
                        Ydatas = np.column_stack((Y_comp, 0 * Y_comp, 0 * Y_comp))
                    else:
                        Y_comp[Xdatas[:, 1] < 0] = -Y_comp[Xdatas[:, 1] < 0]
                        Ydatas = np.column_stack((0 * Y_comp, Y_comp, 0 * Y_comp))
                else:
                    vecfield = self.to_rphiz()
                    result = vecfield.components[component_list[0]].get_along(
                        arg_list,
                        axis_data=axis_data,
                        unit=unit,
                        is_norm=is_norm,
                    )
                    Y_comp = result[vecfield.components[component_list[0]].symbol]

                    if "x" in result and "y" in result:
                        Xdatas = np.column_stack((result["x"], result["y"]))
                        rphiz = xyz_to_rphiz(Xdatas)

                        if component_list[0] == "radial":
                            Y_3d = np.column_stack((Y_comp, 0 * Y_comp, 0 * Y_comp))
                        else:
                            Y_3d = np.column_stack((0 * Y_comp, Y_comp, 0 * Y_comp))

                        Ydatas = rphiz_to_xyz_field(Y_3d, rphiz[:, 1])

                    else:
                        if radius is None:
                            radius = 1
                        phi = result["angle"]
                        rphi = np.column_stack((np.array([radius] * len(phi)), phi))
                        Xdatas = rphiz_to_xyz(rphi)
                        if component_list[0] == "radial":
                            Y_3d = np.column_stack((Y_comp, 0 * Y_comp, 0 * Y_comp))
                        else:
                            Y_3d = np.column_stack((0 * Y_comp, Y_comp, 0 * Y_comp))

                        Ydatas = rphiz_to_xyz_field(Y_3d, phi)

            Ydatas = np.real(Ydatas * np.exp(1j * phase))

            title2 = " for "
            if "time" in result:
                if isinstance(result["time"], str):
                    time_str = result["time"]
                else:
                    time_str = np.array2string(
                        result["time"], formatter={"float_kind": "{:.3g}".format}
                    )
                title2 += (
                    "time="
                    + time_str.replace(" ", ", ").replace("[", "").replace("]", "")
                    + "[s]"
                )
            elif "freqs" in result:
                title2 += (
                    "freqs="
                    + np.array2string(
                        result["freqs"], formatter={"float_kind": "{:.5g}".format}
                    )
                    .replace(" ", ", ")
                    .replace("[", "")
                    .replace("]", "")
                    + "[Hz]"
                )

            title3 = ""
            axes_dict_other = result["axes_dict_other"]
            for axis_name in axes_dict_other:
                is_display = True
                for axis in self.get_axes():
                    if axis.name == axis_name:
                        if (
                            isinstance(axis, DataPattern)
                            and len(axis.unique_indices) == 1
                        ):
                            is_display = False
                if is_display:
                    if isinstance(axes_dict_other[axis_name][0], str):
                        title3 += axis_name + "=" + axes_dict_other[axis_name][0]
                    else:
                        title3 += (
                            axis_name
                            + "="
                            + np.array2string(
                                axes_dict_other[axis_name][0],
                                formatter={"float_kind": "{:.3g}".format},
                            )
                            .replace(" ", ", ")
                            .replace("[", "")
                            .replace("]", "")
                            + " ["
                            + axes_dict_other[axis_name][1]
                            + "], "
                        )
            if title2 == " for " and title3 == "":
                title2 = ""
            title = title + title2 + title3

            # Normalize Ydatas
            # Ydatas = Ydatas / (np_max(Ydatas) * 0.001 * radius)
            plot_2D(
                [Xdatas],
                [Ydatas],
                color_list=color_list,
                linestyle_list=linestyles,
                linewidth_list=linewidth_list,
                title=title,
                legend_list=[self.name],
                xlabel="[m]",
                ylabel="[m]",
                fig=fig,
                ax=ax,
                type_plot="quiver",
                save_path=save_path,
                is_show_fig=is_show_fig,
                win_title=win_title,
                font_name=font_name,
                font_size_title=font_size_title,
                font_size_label=font_size_label,
                font_size_legend=font_size_legend,
                is_show_legend=is_show_legend,
                is_grid=False,
                scale_units=scale_units,
                scale=scale,
                width=width,
                is_outside_legend=is_outside_legend,
                is_frame_legend=is_frame_legend,
            )

        else:
            # Call the plot on each component
            if component_list is None:  # default: extract all components
                component_list = self.components.keys()
            for i, comp in enumerate(component_list):
                # (fig, axes, patch_leg, label_leg) = init_fig(None, shape="rectangle")

                if save_path is not None and len(component_list) > 1:
                    save_path_comp = (
                        save_path.split(".")[0]
                        + "_"
                        + comp
                        + "."
                        + save_path.split(".")[1]
                    )
                else:
                    save_path_comp = save_path

                self.components[comp].plot_2D_Data(
                    arg_list,
                    axis_data=axis_data,
                    is_norm=is_norm,
                    unit=unit,
                    data_list=[dat.components[comp] for dat in data_list],
                    legend_list=legend_list,
                    linestyles=linestyles,
                    color_list=color_list,
                    save_path=save_path_comp,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_disp_title=is_disp_title,
                    is_grid=is_grid,
                    is_auto_ticks=is_auto_ticks,
                    is_auto_range=is_auto_range,
                    fig=fig,
                    ax=ax,
                    barwidth=barwidth,
                    type_plot=type_plot,
                    fund_harm_dict=fund_harm_dict,
                    is_show_fig=is_show_fig,
                    thresh=thresh,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    is_show_legend=is_show_legend,
                    is_outside_legend=is_outside_legend,
                    is_frame_legend=is_frame_legend,
                )

    # cf Methods.SciDataTool.VectorField.plot_2D_Data_Animated
    def plot_2D_Data_Animated(
        self,
        animated_axis,
        *arg_list,
        nb_frames=50,
        fps=10,
        axis_data=None,
        radius=None,
        is_norm=False,
        unit="SI",
        component_list=None,
        data_list=[],
        legend_list=[],
        color_list=None,
        linestyles=None,
        linewidth_list=[1.5],
        save_path=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        is_logscale_x=False,
        is_logscale_y=False,
        is_disp_title=True,
        is_grid=True,
        is_auto_ticks=True,
        is_auto_range=False,
        fig=None,
        ax=None,
        barwidth=100,
        type_plot=None,
        fund_harm_dict=None,
        is_show_fig=None,
        win_title=None,
        thresh=0.02,
        font_name="arial",
        font_size_title=12,
        font_size_label=10,
        font_size_legend=8,
        scale_units="x",
        scale=None,
        width=0.005,
        phase=0,
        is_show_legend=True,
        is_outside_legend=False,
        is_frame_legend=True,
        is_plot_only=False,
    ):
        """Plots a field as a function of time

        Parameters
        ----------
        self : VectorField
            an VectorField object
        Data_str : str
            name of the Data Object to plot (e.g. "mag.Br")
        animated_axis : str
            The field will be animated along this axis
        *arg_list : list of str
            arguments to specify which axes to plot
        nb_frames : int
            number of frames used to build the gif
        fps: int
            frames displayed per second
        radius : float
            radius used for quiver plot
        is_norm : bool
            boolean indicating if the field must be normalized
        unit : str
            unit in which to plot the field
        data_list : list
            list of Data objects to compare
        component_list : list
            list of component names to plot in separate figures
        legend_list : list
            list of legends to use for each Data object (including reference one) instead of data.name
        color_list : list
            list of colors to use for each Data object
        save_path : str
            full path of the png file where the figure is saved if save_path is not None
        x_min : float
            minimum value for the x-axis
        x_max : float
            maximum value for the x-axis
        y_min : float
            minimum value for the y-axis
        y_max : float
            maximum value for the y-axis
        is_logscale_x : bool
            boolean indicating if the x-axis must be set in logarithmic scale
        is_logscale_y : bool
            boolean indicating if the y-axis must be set in logarithmic scale
        is_disp_title : bool
            boolean indicating if the title must be displayed
        is_grid : bool
            boolean indicating if the grid must be displayed
        is_auto_ticks : bool
            in fft, adjust ticks to freqs (deactivate if too close)
        is_auto_range : bool
            in fft, display up to 1% of max
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        barwidth : float
            barwidth scaling factor, only if type_plot = "bargraph"
        type_plot : str
            type of 2D graph : "curve", "bargraph", "barchart" or "quiver"
        fund_harm_dict : dict
            Dict containing axis name as key and frequency/order/wavenumber of fundamental harmonic as value to display fundamental harmonic in red in the fft
        is_show_fig : bool
            True to show figure after plot
        thresh : float
            threshold for automatic fft ticks
        scale : float
            arrow length factor in quiver. Be careful, if scale = None then there will be a normalization on the arrows on each frame
        width : float
            arrow width factor in quiver
        is_plot_only : bool
            True to remove axes, title and legend
        """

        # Special case of quiver plot
        if type_plot == "quiver":
            # list of png to make the gif
            images = list()

            # definition of the step along animated axis
            result = self.get_rphiz_along(animated_axis)
            animated_axis_name = animated_axis.split("[")[0]
            animated_values = result[animated_axis_name]
            value_max = np.nanmax(animated_values)
            value_min = np.nanmin(animated_values)
            variation_step = (value_max - value_min) / nb_frames

            # Getting the name of the gif
            save_path_gif = save_path.replace(".png", ".gif")
            fig.suptitle(None)
            # Copy_fig make a deep copy so that the machine plot is conserved
            deepcopy_fig = copy_fig(fig)

            # Params settings
            save_path = None
            is_show_fig = False

            # for value in animated_values:
            while value_min < value_max - variation_step:
                # Select a frequency and make it rotate by playing on the phase
                if "freqs" in arg_list[0]:
                    arg_list0 = arg_list
                    step = (value_min / variation_step) / nb_frames
                    phase = 2 * np.pi * step

                # or directly select an instant/element in the animated axis
                else:
                    if animated_axis_name in arg_list:
                        arg_listx = list(arg_list)
                        ind_ax = arg_listx.index(animated_axis_name)
                        arg_listx.pop(ind_ax)
                        arg_list0 = (
                            animated_axis_name + "=" + str(value_min),
                        ) + tuple(arg_listx)
                        phase = 0
                    else:
                        arg_list0 = (
                            animated_axis_name + "=" + str(value_min),
                        ) + arg_list
                        phase = 0

                # Call to plot_2D_Data of VectorField class, which manage the quiver case
                self.plot_2D_Data(
                    *arg_list0,
                    axis_data=axis_data,
                    radius=radius,
                    is_norm=is_norm,
                    unit=unit,
                    component_list=component_list,
                    data_list=data_list,
                    legend_list=legend_list,
                    color_list=color_list,
                    linestyles=linestyles,
                    linewidth_list=linewidth_list,
                    save_path=save_path,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_disp_title=False,
                    is_grid=is_grid,
                    is_auto_ticks=is_auto_ticks,
                    is_auto_range=is_auto_range,
                    fig=fig,
                    ax=ax,
                    barwidth=barwidth,
                    type_plot=type_plot,
                    fund_harm_dict=fund_harm_dict,
                    is_show_fig=is_show_fig,
                    win_title=win_title,
                    thresh=thresh,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                    scale=scale,
                    width=width,
                    phase=phase,
                    scale_units=scale_units,
                    is_show_legend=is_show_legend,
                    is_outside_legend=is_outside_legend,
                    is_frame_legend=is_frame_legend,
                )

                if is_plot_only:
                    ax.set_axis_off()
                    ax.set_title("")
                    ax.get_legend().remove()

                fig.canvas.draw()
                image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
                image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                images.append(image)

                # Fig and ax reset to default for background
                fig, ax, _, _ = init_fig()
                deepcopy_ax = deepcopy_fig.axes[0]
                for patch in deepcopy_ax.patches:
                    patch_cpy = copy(patch)
                    patch_cpy.axes = None
                    patch_cpy.figure = None
                    patch_cpy.set_transform(ax.transData)
                    ax.add_patch(patch_cpy)
                ax.set_xlim(deepcopy_ax.get_xlim())
                ax.set_ylim(deepcopy_ax.get_ylim())
                ax.set_xlabel(deepcopy_ax.get_xlabel())
                ax.set_ylabel(deepcopy_ax.get_ylabel())
                ax.set_title(deepcopy_ax.get_title())
                fig.suptitle(None)
                # While condition incrementation
                value_min += variation_step

            # Creating the gif
            plt.close(fig)
            imageio.mimsave(save_path_gif, images, format="GIF-PIL", fps=fps)

        else:
            # Call the plot on each component
            if component_list is None:  # default: extract all components
                component_list = self.components.keys()
            for i, comp in enumerate(component_list):
                # (fig, axes, patch_leg, label_leg) = init_fig(None, shape="rectangle")

                if save_path is not None and len(component_list) > 1:
                    save_path_comp = (
                        save_path.split(".")[0]
                        + "_"
                        + comp
                        + "."
                        + save_path.split(".")[1]
                    )
                else:
                    save_path_comp = save_path

                self.components[comp].plot_2D_Data_Animated(
                    animated_axis,
                    *arg_list,
                    nb_frames=nb_frames,
                    fps=fps,
                    axis_data=axis_data,
                    is_norm=is_norm,
                    unit=unit,
                    data_list=[dat.components[comp] for dat in data_list],
                    legend_list=legend_list,
                    color_list=color_list,
                    save_path=save_path_comp,
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    is_logscale_x=is_logscale_x,
                    is_logscale_y=is_logscale_y,
                    is_disp_title=is_disp_title,
                    is_grid=is_grid,
                    is_auto_ticks=is_auto_ticks,
                    is_auto_range=is_auto_range,
                    fig=fig,
                    ax=ax,
                    barwidth=barwidth,
                    type_plot=type_plot,
                    fund_harm_dict=fund_harm_dict,
                    is_show_fig=is_show_fig,
                    thresh=thresh,
                    font_name=font_name,
                    font_size_title=font_size_title,
                    font_size_label=font_size_label,
                    font_size_legend=font_size_legend,
                )

    # cf Methods.SciDataTool.VectorField.plot_3D_Data
    def plot_3D_Data(
        self,
        *arg_list,
        axis_data=None,
        is_norm=False,
        unit="SI",
        component_list=None,
        save_path=None,
        x_min=None,
        x_max=None,
        y_min=None,
        y_max=None,
        z_min=None,
        z_max=None,
        z_range=None,
        is_auto_ticks=True,
        is_auto_range=False,
        is_2D_view=True,
        is_same_size=False,
        N_stem=100,
        fig=None,
        ax=None,
        is_show_fig=None,
        is_logscale_x=False,
        is_logscale_y=False,
        is_logscale_z=False,
        thresh=None,
        is_switch_axes=False,
        colormap="jet",
        win_title=None,
        font_name="arial",
        font_size_title=12,
        font_size_label=10,
        font_size_legend=8,
    ):
        """Plots a field as a function of time

        Parameters
        ----------
        self : Output
            an Output object
        Data_str : str
            name of the Data Object to plot (e.g. "mag.Br")
        *arg_list : list of str
            arguments to specify which axes to plot
        is_norm : bool
            boolean indicating if the field must be normalized
        unit : str
            unit in which to plot the field
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        x_min : float
            minimum value for the x-axis
        x_max : float
            maximum value for the x-axis
        y_min : float
            minimum value for the y-axis
        y_max : float
            maximum value for the y-axis
        z_min : float
            minimum value for the z-axis
        z_max : float
            maximum value for the z-axis
        is_auto_ticks : bool
            in fft, adjust ticks to freqs (deactivate if too close)
        is_auto_range : bool
            in fft, display up to 1% of max
        is_2D_view : bool
            True to plot Data in xy plane and put z as colormap
        is_same_size : bool
            True to have all color blocks with same size in 2D view
        N_stem : int
            number of harmonics to plot (only for stem plots)
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            ax on which to plot the data
        is_show_fig : bool
            True to show figure after plot
        is_logscale_x : bool
            boolean indicating if the x-axis must be set in logarithmic scale
        is_logscale_y : bool
            boolean indicating if the y-axis must be set in logarithmic scale
        is_logscale_z : bool
            boolean indicating if the z-axis must be set in logarithmic scale
        thresh : float
            threshold for automatic fft ticks
        is_switch_axes : bool
            to switch x and y axes
        """

        # Call the plot on each component
        if component_list is None:  # default: extract all components
            component_list = self.components.keys()
        for i, comp in enumerate(component_list):

            if save_path is not None and len(component_list) > 1:
                save_path_comp = (
                    save_path.split(".")[0] + "_" + comp + "." + save_path.split(".")[1]
                )
            else:
                save_path_comp = save_path

            self.components[comp].plot_3D_Data(
                arg_list,
                axis_data=axis_data,
                is_norm=is_norm,
                unit=unit,
                save_path=save_path_comp,
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max,
                z_min=z_min,
                z_max=z_max,
                colormap=colormap,
                is_auto_ticks=is_auto_ticks,
                is_auto_range=is_auto_range,
                is_2D_view=is_2D_view,
                is_same_size=is_same_size,
                N_stem=N_stem,
                fig=fig,
                ax=ax,
                is_show_fig=is_show_fig,
                is_logscale_x=is_logscale_x,
                is_logscale_y=is_logscale_y,
                is_logscale_z=is_logscale_z,
                thresh=thresh,
                is_switch_axes=is_switch_axes,
                win_title=win_title,
                font_name=font_name,
                font_size_title=font_size_title,
                font_size_label=font_size_label,
                font_size_legend=font_size_legend,
            )

    # cf Methods.SciDataTool.VectorField.time_to_freq
    def time_to_freq(self):
        """Performs the Fourier Transform and stores the resulting field in a VectorField of DataFreq objects.
        Parameters
        ----------
        self : VectorField
            a VectorField object
        Returns
        -------
        a VectorField object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
        VectorField = module.VectorField

        comp_dict = dict()
        for key, comp in self.components.items():
            comp_dict[key] = comp.time_to_freq()

        return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    # cf Methods.SciDataTool.VectorField.to_rphiz
    def to_rphiz(self):
        """Performs the corrdinate change and stores the resulting field in a VectorField object.
        Parameters
        ----------
        self : VectorField
            a VectorField object
        Returns
        -------
        a VectorField object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
        VectorField = module.VectorField

        if (
            "radial" in self.components
            or "tangential" in self.components
            or "axial" in self.components
        ):
            return self.copy()

        else:
            # Coordinate transform
            arg_list = [
                (
                    axis.name
                    if axis.name in ["freqs", "wavenumber"]
                    else axis.name + "[smallestperiod]"
                )
                for axis in self.components["comp_x"].axes
            ]
            result = self.get_rphiz_along(*arg_list)
            # Store in new VectorField
            comp_dict = dict()

            Comp_r = self.components["comp_x"].copy()
            Comp_r.name = "Radial " + self.components["comp_x"].name.lower().replace(
                " along x-axis", ""
            )
            Comp_r.symbol = self.components["comp_x"].symbol.replace("_x", "_r")
            Comp_r.values = result["radial"]
            comp_dict["radial"] = Comp_r

            Comp_t = self.components["comp_x"].copy()
            Comp_t.name = "Tangential " + self.components[
                "comp_x"
            ].name.lower().replace(" along x-axis", "")
            Comp_t.symbol = self.components["comp_x"].symbol.replace("_r", "_y")
            Comp_t.values = result["tangential"]
            comp_dict["comp_y"] = Comp_t

            if "axial" in self.components:
                Comp_z = self.components["axial"].copy()
                comp_dict["comp_z"] = Comp_z

            return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    # cf Methods.SciDataTool.VectorField.to_xyz
    def to_xyz(self):
        """Performs the corrdinate change and stores the resulting field in a VectorField object.
        Parameters
        ----------
        self : VectorField
            a VectorField object
        Returns
        -------
        a VectorField object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.VectorField", fromlist=["VectorField"])
        VectorField = module.VectorField

        if "comp_x" in self.components or "comp_y" in self.components:
            return self.copy()

        else:
            # Coordinate transform
            arg_list = [
                (
                    axis.name
                    if axis.name in ["freqs", "wavenumber"]
                    else axis.name + "[smallestperiod]"
                )
                for axis in self.components["radial"].axes
            ]
            result = self.get_xyz_along(*arg_list, is_squeeze=False)
            # Store in new VectorField
            comp_dict = dict()

            Comp_x = self.components["radial"].copy()
            Comp_x.name = (
                self.components["radial"].name.lower().replace("radial ", "")
                + " along x-axis"
            )
            Comp_x.symbol = self.components["radial"].symbol.replace("_r", "_x")
            Comp_x.values = result["comp_x"]
            comp_dict["comp_x"] = Comp_x

            Comp_y = self.components["radial"].copy()
            Comp_y.name = (
                self.components["radial"].name.lower().replace("radial ", "")
                + " along y-axis"
            )
            Comp_y.symbol = self.components["radial"].symbol.replace("_r", "_y")
            Comp_y.values = result["comp_y"]
            comp_dict["comp_y"] = Comp_y

            if "axial" in self.components:
                Comp_z = self.components["axial"].copy()
                comp_dict["comp_z"] = Comp_z

            return VectorField(name=self.name, symbol=self.symbol, components=comp_dict)

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, name="", symbol="", components=-1, init_dict=None, init_str=None
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
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "symbol" in list(init_dict.keys()):
                symbol = init_dict["symbol"]
            if "components" in list(init_dict.keys()):
                components = init_dict["components"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.name = name
        self.symbol = symbol
        self.components = components

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VectorField_str = ""
        if self.parent is None:
            VectorField_str += "parent = None " + linesep
        else:
            VectorField_str += (
                "parent = " + str(type(self.parent)) + " object" + linesep
            )
        VectorField_str += 'name = "' + str(self.name) + '"' + linesep
        VectorField_str += 'symbol = "' + str(self.symbol) + '"' + linesep
        if len(self.components) == 0:
            VectorField_str += "components = dict()" + linesep
        for key, obj in self.components.items():
            tmp = (
                self.components[key].__str__().replace(linesep, linesep + "\t")
                + linesep
            )
            VectorField_str += "components[" + key + "] =" + tmp + linesep + linesep
        return VectorField_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.name != self.name:
            return False
        if other.symbol != self.symbol:
            return False
        if other.components != self.components:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._name != self._name:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._name) + ", other=" + str(other._name) + ")"
                )
                diff_list.append(name + ".name" + val_str)
            else:
                diff_list.append(name + ".name")
        if other._symbol != self._symbol:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._symbol)
                    + ", other="
                    + str(other._symbol)
                    + ")"
                )
                diff_list.append(name + ".symbol" + val_str)
            else:
                diff_list.append(name + ".symbol")
        if (other.components is None and self.components is not None) or (
            other.components is not None and self.components is None
        ):
            diff_list.append(name + ".components None mismatch")
        elif self.components is None:
            pass
        elif len(other.components) != len(self.components):
            diff_list.append("len(" + name + "components)")
        else:
            for key in self.components:
                diff_list.extend(
                    self.components[key].compare(
                        other.components[key],
                        name=name + ".components[" + str(key) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.name)
        S += getsizeof(self.symbol)
        if self.components is not None:
            for key, value in self.components.items():
                S += getsizeof(value) + getsizeof(key)
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

        VectorField_dict = dict()
        VectorField_dict["name"] = self.name
        VectorField_dict["symbol"] = self.symbol
        if self.components is None:
            VectorField_dict["components"] = None
        else:
            VectorField_dict["components"] = dict()
            for key, obj in self.components.items():
                if obj is not None:
                    VectorField_dict["components"][key] = obj.as_dict(
                        type_handle_ndarray=type_handle_ndarray,
                        keep_function=keep_function,
                        **kwargs,
                    )
                else:
                    VectorField_dict["components"][key] = None
        # The class name is added to the dict for deserialisation purpose
        VectorField_dict["__class__"] = "VectorField"
        return VectorField_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        name_val = self.name
        symbol_val = self.symbol
        if self.components is None:
            components_val = None
        else:
            components_val = dict()
            for key, obj in self.components.items():
                components_val[key] = obj.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            name=name_val, symbol=symbol_val, components=components_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.name = None
        self.symbol = None
        self.components = None

    def _get_name(self):
        """getter of name"""
        return self._name

    def _set_name(self, value):
        """setter of name"""
        check_var("name", value, "str")
        self._name = value

    name = property(
        fget=_get_name,
        fset=_set_name,
        doc="""Name of the vector field

        :Type: str
        """,
    )

    def _get_symbol(self):
        """getter of symbol"""
        return self._symbol

    def _set_symbol(self, value):
        """setter of symbol"""
        check_var("symbol", value, "str")
        self._symbol = value

    symbol = property(
        fget=_get_symbol,
        fset=_set_symbol,
        doc="""Symbol of the vector field

        :Type: str
        """,
    )

    def _get_components(self):
        """getter of components"""
        if self._components is not None:
            for key, obj in self._components.items():
                if obj is not None:
                    obj.parent = self
        return self._components

    def _set_components(self, value):
        """setter of components"""
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
                        "pyleecan.Classes", obj.get("__class__"), "components"
                    )
                    value[key] = class_obj(init_dict=obj)
        if type(value) is int and value == -1:
            value = dict()
        check_var("components", value, "{DataND}")
        self._components = value

    components = property(
        fget=_get_components,
        fset=_set_components,
        doc="""Dict of the components

        :Type: {DataND}
        """,
    )
