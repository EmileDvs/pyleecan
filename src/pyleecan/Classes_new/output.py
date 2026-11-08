# Experimental dataclass generated from Generator/ClassesRef/Output/Output.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass
from sys import getsizeof

import numpy as np
from scipy.io import savemat

from ..definitions import RESULT_DIR, config_dict
from ..Functions.Load.import_class import import_class
from ..Functions.Plot import fft_dict
from ..Functions.Plot.Pyvista.configure_plot import configure_plot
from ..Functions.Plot.Pyvista.plot_mesh_field import plot_mesh_field
from ._pyleecan_class import PyleecanClass
from .norm_affine import NormAffine
from .norm_vector import NormVector
from .out_elec import OutElec
from .out_force import OutForce
from .out_geo import OutGeo
from .out_geo_lam import OutGeoLam
from .out_loss import OutLoss
from .out_mag import OutMag
from .out_post import OutPost
from .out_struct import OutStruct
from .simulation import Simulation


@dataclass(eq=False)
class Output(PyleecanClass):
    """Main Output object: gather all the outputs of all the modules

    Attributes
    ----------
    simu : Simulation or None
        Simulation object that generated the Output
        Default: None
    path_result : str or None
        Path to the folder to same the results
        Default: None
    geo : OutGeo or None
        Geometry output
        Default: None
    elec : OutElec or None
        Electrical module output
        Default: None
    mag : OutMag or None
        Magnetic module output
        Default: None
    struct : OutStruct or None
        Structural module output
        Default: None
    post : OutPost or None
        Post-Processing settings
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Output"
    force : OutForce or None
        Force module output
        Default: None
    loss : OutLoss or None
        Loss module output
        Default: None
    """

    COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]
    FONT_FAMILY_PYVISTA = config_dict["PLOT"]["FONT_FAMILY_PYVISTA"]
    simu: Simulation | None = None
    """Simulation object that generated the Output"""
    path_result: str | None = None
    """Path to the folder to same the results"""
    geo: OutGeo | None = None
    """Geometry output"""
    elec: OutElec | None = None
    """Electrical module output"""
    mag: OutMag | None = None
    """Magnetic module output"""
    struct: OutStruct | None = None
    """Structural module output"""
    post: OutPost | None = None
    """Post-Processing settings"""
    logger_name: str = "Pyleecan.Output"
    """Name of the logger to use"""
    force: OutForce | None = None
    """Force module output"""
    loss: OutLoss | None = None
    """Loss module output"""

    # Inlined from Methods.Output.Output.getter.comp_angle_rotor
    def comp_angle_rotor(self, Time):
        """Computes the angular position of the rotor as a function of time and set it as normalization
        (should not happen since angle_rotor is already added in Time normalizations in Input.comp_axis_time)

        Parameters
        ----------
        self : Output
            an Output object
        Time : Data
            a time axis (SciDataTool Data object)
        rot_dir: int
            Rotor rotating direction (by default -1: clockwise)

        Returns
        -------
        angle_rotor: ndarray
            angular position of the rotor as a function of time (vector) [rad]

        """

        # Get rotor rotating direction
        rot_dir = self.geo.rot_dir

        # Compute according to the speed
        Nr = self.elec.get_Nr(Time=Time)

        # Compute rotor initial angle (for synchronous machines, to align rotor d-axis and stator alpha-axis)
        A0 = self.get_angle_rotor_initial()

        # Case where normalization is a constant
        if np.unique(Nr).size == 1:
            # Define affine normalization between time and rotor angle
            Time.normalizations["angle_rotor"] = NormAffine(
                slope=rot_dir * Nr[0] * 360 / 60, offset=A0 * 180 / np.pi
            )
            # Compute rotor angle array from normalization
            angle_rotor = Time.get_values(normalization="angle_rotor") * np.pi / 180

        else:
            # Calculate rotor angle from spee
            time = Time.get_values(is_smallestperiod=True)
            if time.size == 1:
                # Only one time step, no need to compute the position
                angle_rotor = np.array([A0])
            else:
                deltaT = time[1] - time[0]
                # Convert Nr from [rpm] to [rad/s] (time in [s] and angle_rotor in [rad])
                Ar = np.cumsum(rot_dir * deltaT * Nr * 2 * np.pi / 60)
                # Enforce first position to 0
                Ar = np.roll(Ar, 1)
                Ar[0] = 0
                angle_rotor = Ar + A0
            # Define vector normalization between time and rotor angle
            Time.normalizations["angle_rotor"] = NormVector(vector=angle_rotor)

        return angle_rotor

    # Inlined from Methods.Output.Output.getter.export_to_mat
    def export_to_mat(self, file_path):
        """Export the main outputs to a .mat file


        Parameters
        ----------
        self : Output
            An Output object
        file_path : str
            Path to save the generated mat file
        """

        # Dict to save
        data_dict = {}

        # Data size
        data_dict["Na_tot"] = self.simu.input.Na_tot
        data_dict["Nt_tot"] = self.simu.input.Nt_tot

        # Electrical data
        if self.elec is not None:
            if self.elec.OP is not None:
                data_dict["N0"] = self.elec.OP.N0
                I_dict = self.elec.OP.get_Id_Iq()
                data_dict["Id"] = I_dict["Id"]
                data_dict["Iq"] = I_dict["Iq"]
                if hasattr(self.elec.OP, "If_ref"):
                    data_dict["If"] = self.elec.OP.If_ref
                Is = self.elec.get_Is()
                if Is is not None:
                    data_dict["Is"] = Is.get_along("phase", "time")["I_s"]
        # Magnetic data
        if self.mag is not None:
            data_dict["time"] = self.mag.axes_dict["time"].get_values()
            data_dict["angle"] = self.mag.axes_dict["angle"].get_values()
            if self.mag.B is not None:
                data_dict["B_rad"] = self.mag.B.components["radial"].get_along(
                    "time", "angle"
                )["B_{rad}"]
                data_dict["B_tan"] = self.mag.B.components["tangential"].get_along(
                    "time", "angle"
                )["B_{circ}"]
            if self.mag.Tem is not None:
                data_dict["Tem"] = self.mag.Tem.get_along("time")["T_{em}"]
            if self.mag.Tem_av is not None:
                data_dict["Tem_av"] = self.mag.Tem_av
            if self.mag.Tem_rip_norm is not None:
                data_dict["Tem_rip_norm"] = self.mag.Tem_rip_norm
            if self.mag.Tem_rip_pp is not None:
                data_dict["Tem_rip_pp"] = self.mag.Tem_rip_pp
            if self.mag.Phi_wind_stator is not None:
                data_dict["Phi_wind_stator"] = self.mag.Phi_wind_stator.get_along(
                    "time", "phase"
                )["Phi_{wind}"]
            # if self.mag.emf is not None:
            #     data_dict["emf"] = self.mag.emf.get_along("time")
        # Save result
        savemat(file_path, data_dict)

    # Inlined from Methods.Output.Output.getter.get_angle_rotor
    def get_angle_rotor(self, Time=None):
        """Return the angular position of the rotor as a function of time from Time normalizations
        and or calculate angle_rotor and add it to Time normalization

        Parameters
        ----------
        self : Output
            an Output object
        Time: Data
            a time axis (SciDataTool Data object)

        Returns
        -------
        angle_rotor: ndarray
            angular position of the rotor as a function of time (vector) [rad]

        """

        # time axis is not provided -> use elec or mag time axis
        if Time is None:
            if self.elec.axes_dict is not None and "time" in self.elec.axes_dict:
                Time = self.elec.axes_dict["time"]
            elif self.mag.axes_dict is not None and "time" in self.mag.axes_dict:
                Time = self.mag.axes_dict["time"]
            else:
                raise Exception("No time axis given, cannot compute rotor angle")

        if "angle_rotor" in Time.normalizations:
            # angle rotor is stored in degrees as normalization of Time axis
            angle_rotor = Time.get_values(normalization="angle_rotor") * np.pi / 180
        else:
            # Recalculate rotor angular position over time (should not happen)
            self.get_logger().warning(
                "angle_rotor not in time normalizations, recalculate rotor angular position over time and add it to normalizations"
            )
            angle_rotor = self.comp_angle_rotor(Time)

        return angle_rotor

    # Inlined from Methods.Output.Output.getter.get_angle_rotor_initial
    def get_angle_rotor_initial(self):
        """Return the difference between the d axis angle of the stator and the rotor

        Parameters
        ----------
        self : Output
            an Output object

        Returns
        -------
        angle_rotor_initial: float
            difference between the d axis angle of the stator and the rotor [rad]

        """

        # Already available => Return
        if self.geo.angle_rotor_initial is not None:
            return self.geo.angle_rotor_initial
        else:  # Compute
            self.geo.angle_rotor_initial = self.simu.machine.comp_angle_rotor_initial()
            return self.geo.angle_rotor_initial

    # Inlined from Methods.Output.Output.getter.get_BH_rotor
    def get_BH_rotor(self):
        """Return the B(H) curve of the rotor material

        Parameters
        ----------
        self : Output
            an Output object

        Returns
        -------
        BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """

        # Already available => Return
        if (
            self.geo is not None
            and self.geo.rotor is not None
            and self.geo.rotor.BH_curve is not None
        ):
            return self.geo.rotor.BH_curve

        # Check if possible to get the BH curve
        if (
            self.simu is None
            or self.simu.machine is None
            or self.simu.machine.rotor is None
            or self.simu.machine.rotor.mat_type is None
        ):
            raise self.GetOutError(
                "Output.simu.machine.rotor.mat_type is not Set, can't get the B(H) curve"
            )
        mat_type = self.simu.machine.rotor.mat_type
        if mat_type.mag is None:
            raise self.GetOutError("rotor materials magnetic property is not set")

        # Compute and store the BH curve
        BH = mat_type.mag.get_BH()
        if self.geo.rotor is None:
            self.geo.rotor = OutGeoLam()
            self.geo.rotor._set_None()
        self.geo.rotor.BH_curve = BH

        return BH

    # Inlined from Methods.Output.Output.getter.get_BH_stator
    def get_BH_stator(self):
        """Return the B(H) curve of the stator material

        Parameters
        ----------
        self : Output
            an Output object

        Returns
        -------
        BH: numpy.ndarray
            B(H) values (two colums matrix: H and B(H))

        """

        # Already available => Return
        if (
            self.geo is not None
            and self.geo.stator is not None
            and self.geo.stator.BH_curve is not None
        ):
            return self.geo.stator.BH_curve

        # Check if possible to get the BH curve
        if (
            self.simu is None
            or self.simu.machine is None
            or self.simu.machine.stator is None
            or self.simu.machine.stator.mat_type is None
        ):
            raise self.GetOutError(
                "Output.simu.machine.stator.mat_type is not Set, can't get the B(H) curve"
            )
        mat_type = self.simu.machine.stator.mat_type
        if mat_type.mag is None:
            raise self.GetOutError("stator materials magnetic property is not set")

        # Compute and store the BH curve
        BH = mat_type.mag.get_BH()
        if self.geo.stator is None:
            self.geo.stator = OutGeoLam()
            self.geo.stator._set_None()
        self.geo.stator.BH_curve = BH

        return BH

    # Inlined from Methods.Output.Output.getter.get_data_from_str
    def get_data_from_str(self, data_str):
        """Return the data object corresponding to the data str

        Parameters
        ----------
        self : Output
            an Output object
        data_str : string
            a string corresponding to a data object

        Returns
        -------
        data : Data
            a Data object

        """

        # Get Data object names
        phys = getattr(self, data_str.split(".")[0])
        if "get_" in data_str.split(".")[1]:  # get method
            if "[" in data_str.split(".")[1]:  # dict
                d = getattr(phys, data_str.split(".")[1].split("[")[0])()
                data = d[data_str.split("[")[1].rstrip("]")]
            else:
                data = getattr(phys, data_str.split(".")[1])()
        elif "[" in data_str.split(".")[1]:  # dict
            d = getattr(phys, data_str.split(".")[1].split("[")[0])
            data = d[data_str.split(".")[1].split("[")[1].rstrip("]")]
        else:
            data = getattr(phys, data_str.split(".")[1])

        # If dict with no specified key -> take first key
        if isinstance(data, dict):
            data2 = data[list(data.keys())[0]]
        else:
            data2 = data

        return data2

    # Inlined from Methods.Output.Output.getter.get_fund_harm
    def get_fund_harm(self, data):
        """Return the fundamental harmonic of the physical quantity in the data object

        Parameters
        ----------
        self : Output
            an Output object
        data : Data
            a Data object

        Returns
        -------
        fund_harm: dict
            Dict containing axis name as key and frequency/order/wavenumber of fundamental harmonic as value

        """

        if data.symbol in ["B", "AGSF", "Is", "Phi_{wind}"]:
            # Init output dict
            fund_harm = {}

            axes_list = data.get_axes()

            # Get machine pole pair number
            p = self.simu.machine.get_pole_pair_number()

            # Get electrical fundamental frequency
            f_elec = self.elec.OP.get_felec()

            # Loop on axes to express the fundamental harmonic of the Data object
            # including normalizations
            for axe in axes_list:
                # Init fundamental value to None for current axis
                coeff = None
                is_match = False

                # Search if the current axis in SciDataTool axis dictionary
                if axe.name in fft_dict.keys():
                    # If yes, find the axis name of the fft
                    axe_fft = fft_dict[axe.name]
                    is_match = True
                elif axe.name in fft_dict.values():
                    axe_fft = axe.name
                    is_match = True

                if is_match:
                    # Assign fundamental value depending on axis name
                    if axe_fft == "freqs":
                        coeff = f_elec
                        axe_fft = "frequency"
                    elif axe_fft == "wavenumber":
                        coeff = p

                    # Add in fund_harm dict the values with different normalizations
                    if coeff is not None:
                        # Assign fundamental value depending on physical quantity
                        if data.symbol == "AGSF":
                            coeff = 2 * coeff
                        # Store value in dict
                        fund_harm[axe_fft] = coeff

                        # Add also normalizations in dict
                        for key, norm in axe.normalizations.items():
                            fund_harm[key] = norm.normalize(fund_harm[axe_fft])

        # Cannot calculate dict of fundamental harmonic values
        else:
            fund_harm = None

        return fund_harm

    # Inlined from Methods.Output.Output.getter.get_machine_periodicity
    def get_machine_periodicity(self, is_rotor_ref=False):
        """Return / Compute the (anti)-periodicities of the machine in time and space domain

        Parameters
        ----------
        self : Output
            An Output object

        Returns
        -------
        per_a : int
            Number of space periodicities of the machine over 2*pi
        is_antisym_a : bool
            True if an anti-periodicity is possible after the space periodicities
        per_t : int
            Number of time periodicities of the machine over time period (p/felec by default if Nrev is None) in static or rotating referential
        is_antisym_t : bool
            True if an anti-periodicity is possible after the time periodicities (in static or rotating referential)
        """

        if (
            self.geo.per_a is None
            or self.geo.is_antiper_a is None
            or self.geo.per_t_S is None
            or self.geo.is_antiper_t_S is None
            or self.geo.per_t_R is None
            or self.geo.is_antiper_t_R is None
        ):
            # Spatial periodicities
            (
                self.geo.per_a,
                self.geo.is_antiper_a,
            ) = self.simu.machine.comp_periodicity_spatial()

            # Time periodicities in both static and rotating referentials
            (
                self.geo.per_t_S,
                self.geo.is_antiper_t_S,
                self.geo.per_t_R,
                self.geo.is_antiper_t_R,
            ) = self.simu.machine.comp_periodicity_time(slip=self.elec.OP.get_slip())

        if is_rotor_ref:
            return (
                self.geo.per_a,
                self.geo.is_antiper_a,
                self.geo.per_t_R,
                self.geo.is_antiper_t_R,
            )

        else:
            return (
                self.geo.per_a,
                self.geo.is_antiper_a,
                self.geo.per_t_S,
                self.geo.is_antiper_t_S,
            )

    # Inlined from Methods.Output.Output.getter.get_path_result
    def get_path_result(self):
        """Return the path to the result folder. If there is a name for the simulation, the path leads to a sub-folder of
        'Results' folder which has the same name. If this sub-folder does not exist, it creates it.

        Parameters
        ----------
        self : Output
            an Output object

        Returns
        -------
        res_path: str
            path to the result folder
        """

        if self.path_result in [None, ""]:
            if self.simu.path_result is not None:
                self.path_result = self.simu.path_result.replace("\\", "/")
            else:
                # If the path doesn't exist, set the default one
                self.path_result = os.path.abspath(
                    os.path.join(RESULT_DIR, self.simu.name)
                )
            if not os.path.isdir(self.path_result):
                os.makedirs(self.path_result)  # Make sure that the folder exist
        return self.path_result

    # Inlined from Methods.Output.Output.plot.Magnetic.plot_B_mesh
    def plot_B_mesh(
        self,
        *args,
        indices=None,
        is_surf=False,
        is_radial=False,
        is_center=False,
        clim=None,
        field_name=None,
        group_names=None,
        save_path=None,
        is_show_fig=True,
        win_title=None,
        is_animated=False,
        title="",
        pv_plotter=None,
        is_contour=True,
        is_2D=False,
    ):
        """Plot the contour of a field on a mesh using pyvista plotter.

        Parameters
        ----------
        self : MeshSolution
            a MeshSolution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        label : str
            a label
        index : int
            an index
        indices : list
            list of the points to extract (optional)
        is_surf : bool
            field over outer surface
        is_radial : bool
            radial component only
        is_center : bool
            field at element-centers
        clim : list
            a list of 2 elements for the limits of the colorbar
        field_name : str
            title of the field to display on plot
        group_names : list
            a list of str corresponding to group name(s)
        save_path : str
            path to save the figure
        is_show_fig : bool
            To call show at the end of the method
        is_animated : True to animate magnetic flux density
        is_2D : bool
            True plot in 2 dimensions (view on XY)

        Returns
        -------

        """
        MS_B = self.mag.meshsolution

        if group_names is not None:
            MS_B_plot = MS_B.get_group(group_names)
        else:
            MS_B_plot = MS_B

        # Init figure
        if pv_plotter is None:
            if title != "" and win_title == "":
                win_title = title
            elif win_title != "" and title == "":
                title = win_title

            pv_plotter, sargs = configure_plot(
                pv_plotter=pv_plotter,
                win_title=win_title,
            )

            pv_plotter.add_text(
                title,
                position="upper_edge",
                color="black",
                font_size=10,
                font=self.FONT_FAMILY_PYVISTA,
            )

        # Get the mesh_pv and field
        mesh_pv, field, field_name = MS_B_plot.get_mesh_field_pv(
            *args,
            label="B",
            indices=indices,
            is_surf=is_surf,
            is_radial=is_radial,
            is_center=is_center,
            field_name=field_name,
        )

        # Add field to mesh
        # if is_surf:
        #     surf = mesh_pv.get_surf(indices=indices)
        #     surf[field_name] = real(field)
        #     mesh_field = surf
        # else:
        #     mesh_pv[field_name] = real(field)
        #     mesh_field = mesh_pv
        if clim is None:
            clim = [np.min(np.real(field)), np.max(np.real(field))]
            if (clim[1] - clim[0]) / clim[1] < 0.01:
                clim[0] = -abs(clim[1])
                clim[1] = abs(clim[1])

        if is_2D:
            # 2D view
            pv_plotter.view_xy()

        plot_mesh_field(
            pv_plotter,
            sargs,
            field_name,
            clim=clim,
            mesh_pv=mesh_pv,
            field=field,
        )

        if is_contour:
            if MS_B_plot["A_z"].type_element != "node":
                raise Exception(
                    "Cannot field lines if A_z calculated on nodes is not in meshsolution"
                )
            mesh_pv_Az, field_A, field_name_A = MS_B_plot.get_mesh_field_pv(
                *args,
                label="A_z",
                indices=indices,
                is_surf=is_surf,
                is_radial=is_radial,
                is_center=is_center,
                field_name=field_name,
            )
            mesh_pv_Az[field_name_A] = field_A
            contours = mesh_pv_Az.contour()
            pv_plotter.add_mesh(contours, color="black", line_width=5)

        ###########
        # Internal animation (cannot be combined with other plots)
        if is_animated:
            pv_plotter.add_text(
                'Adjust 3D view and press "Q"',
                position="lower_edge",
                color="gray",
                font_size=10,
                font="arial",
            )
            pv_plotter.show(auto_close=False)

            pv_plotter.open_gif(save_path)
            pv_plotter.clear()

            if len(args) == 0 or "time" in args:
                mesh_pv_B, field_B, field_name_B = MS_B_plot.get_mesh_field_pv(
                    "time",
                    label="B",
                    indices=indices,
                )
                nframe = len(field_B)
                is_time = True

                if is_contour:
                    mesh_pv_Az, field_A, field_name_A = MS_B_plot.get_mesh_field_pv(
                        "time",
                        label="A_z",
                        indices=indices,
                    )
            else:
                nframe = 25
                mesh_pv_B, field_B, field_name_B = MS_B_plot.get_mesh_field_pv(args)
                is_time = False
                t = np.linspace(0.0, 1.0, nframe + 1)[:nframe]

            for i in range(nframe):
                # Compute colorbar boundaries

                if is_time:
                    field = field_B[i, :]
                    phase = 1
                    if is_contour:
                        field_At = field_A[i, :]
                else:
                    field = field_B
                    phase = np.exp(1j * 2 * np.pi * t[i])

                    if is_contour:
                        field_At = field_A
                # Compute pyvista object
                plot_mesh_field(
                    pv_plotter,
                    sargs,
                    field_name_B,
                    clim=clim,
                    mesh_pv=mesh_pv_B,
                    field=field,
                    phase=phase,
                )

                if is_contour:
                    mesh_pv_Az[field_name_A] = np.real(field_At * phase)
                    contours = mesh_pv_Az.contour()
                    pv_plotter.add_mesh(contours, color="black", line_width=5)

                pv_plotter.add_text(
                    title,
                    position="upper_edge",
                    color="black",
                    font_size=10,
                    font="arial",
                )
                pv_plotter.write_frame()
                pv_plotter.clear()
            pv_plotter.close()

        else:
            # Save figure
            if save_path is None and is_show_fig:
                pv_plotter.show()
            elif save_path is not None:
                pv_plotter.reset_camera()
                pv_plotter.show(interactive=False, screenshot=save_path)

    # Inlined from Methods.Output.Output.print_memory
    def print_memory(self, tab_level=0, detail_level=1, is_print=True):
        """Print an estimation of the memory usage for each property of the object

        Parameters
        ----------
        self : Output
            An Output object
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

        Output = import_class("pyleecan.Classes", "Output")
        if type(self) is Output:
            mem_str = tab + "Total Output size: " + str(getsizeof(self)) + " o\n"
        else:  # XOutput (print only the Output part of the size)
            mem_str = (
                tab + "Total Output size: " + str(Output.__sizeof__(self)) + " o\n"
            )
        if detail_level == 0:
            print(mem_str)
            return
        mem_str += tab + "path_result: " + str(getsizeof(self.path_result)) + " o\n"
        mem_str += tab + "logger_name: " + str(getsizeof(self.logger_name)) + " o\n"

        mem_str += tab + "simu: " + str(getsizeof(self.simu)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "simu", tab_level=tab_level + 1)

        mem_str += tab + "geo: " + str(getsizeof(self.geo)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "geo", tab_level=tab_level + 1)

        mem_str += tab + "elec: " + str(getsizeof(self.elec)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "elec", tab_level=tab_level + 1)

        mem_str += tab + "mag: " + str(getsizeof(self.mag)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "mag", tab_level=tab_level + 1)

        mem_str += tab + "force: " + str(getsizeof(self.force)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "force", tab_level=tab_level + 1)

        mem_str += tab + "struct: " + str(getsizeof(self.struct)) + " o\n"
        if detail_level > 1:
            mem_str += self.detail_prop(self, "struct", tab_level=tab_level + 1)

        mem_str += tab + "post: " + str(getsizeof(self.post)) + " o\n"

        if is_print:
            print(mem_str)
        else:
            return mem_str

    @staticmethod
    def detail_prop(self, prop_name, tab_level=1):
        """Detail the content of the property"""

        tab = ""
        for _ in range(tab_level):
            tab += "    "

        mem_str = ""
        prop = getattr(self, prop_name)
        for attr in dir(prop):
            if (
                # Not method
                not callable(getattr(prop, attr))
                # Not private properties
                and not attr.startswith("_")
                # Not following properties
                and attr not in ["VERSION", "logger_name", "parent"]
            ):
                mem_str += (
                    tab
                    + prop_name
                    + "."
                    + attr
                    + ": "
                    + str(getsizeof(getattr(prop, attr)))
                    + " o\n"
                )
        return mem_str

    class GetOutError(Exception):
        """Raised when an output can't be returned"""
