# File generated according to Generator/ClassesRef/Output/Output.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Output/Output"""

from os import linesep, makedirs
from os.path import abspath, isdir, join
from sys import getsizeof

import numpy as np
from scipy.io import savemat

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Classes.Norm_affine import Norm_affine
from pyleecan.Classes.Norm_vector import Norm_vector
from pyleecan.Classes.OutGeoLam import OutGeoLam
from pyleecan.definitions import RESULT_DIR, config_dict
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot import fft_dict
from pyleecan.Functions.Plot.Pyvista.configure_plot import configure_plot
from pyleecan.Functions.Plot.Pyvista.plot_mesh_field import plot_mesh_field
from pyleecan.Functions.save import save


class Output(FrozenClass):
    """Main Output object: gather all the outputs of all the modules"""

    VERSION = 1
    COLOR_MAP = config_dict["PLOT"]["COLOR_DICT"]["COLOR_MAP"]
    FONT_FAMILY_PYVISTA = config_dict["PLOT"]["FONT_FAMILY_PYVISTA"]

    # cf Methods.Output.Output.getter.comp_angle_rotor
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
            Time.normalizations["angle_rotor"] = Norm_affine(
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
            Time.normalizations["angle_rotor"] = Norm_vector(vector=angle_rotor)

        return angle_rotor

    # cf Methods.Output.Output.getter.export_to_mat
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
        data_dict = dict()

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

    # cf Methods.Output.Output.getter.get_angle_rotor
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

    # cf Methods.Output.Output.getter.get_angle_rotor_initial
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

    # cf Methods.Output.Output.getter.get_BH_rotor
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
            raise GetOutError(
                "Output.simu.machine.rotor.mat_type is not Set, can't get the B(H) curve"
            )
        mat_type = self.simu.machine.rotor.mat_type
        if mat_type.mag is None:
            raise GetOutError("rotor materials magnetic property is not set")

        # Compute and store the BH curve
        BH = mat_type.mag.get_BH()
        if self.geo.rotor is None:
            self.geo.rotor = OutGeoLam()
            self.geo.rotor._set_None()
        self.geo.rotor.BH_curve = BH

        return BH

    # cf Methods.Output.Output.getter.get_BH_stator
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
            raise GetOutError(
                "Output.simu.machine.stator.mat_type is not Set, can't get the B(H) curve"
            )
        mat_type = self.simu.machine.stator.mat_type
        if mat_type.mag is None:
            raise GetOutError("stator materials magnetic property is not set")

        # Compute and store the BH curve
        BH = mat_type.mag.get_BH()
        if self.geo.stator is None:
            self.geo.stator = OutGeoLam()
            self.geo.stator._set_None()
        self.geo.stator.BH_curve = BH

        return BH

    # cf Methods.Output.Output.getter.get_data_from_str
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

    # cf Methods.Output.Output.getter.get_fund_harm
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
            fund_harm = dict()

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

    # cf Methods.Output.Output.getter.get_machine_periodicity
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

    # cf Methods.Output.Output.getter.get_path_result
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
                self.path_result = abspath(join(RESULT_DIR, self.simu.name))
            if not isdir(self.path_result):
                makedirs(self.path_result)  # Make sure that the folder exist
        return self.path_result

    # cf Methods.Output.Output.plot.Magnetic.plot_B_mesh
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
        is_2D=False
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

    # cf Methods.Output.Output.print_memory
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
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
        self.parent = None
        self.simu = simu
        self.path_result = path_result
        self.geo = geo
        self.elec = elec
        self.mag = mag
        self.struct = struct
        self.post = post
        self.logger_name = logger_name
        self.force = force
        self.loss = loss

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Output_str = ""
        if self.parent is None:
            Output_str += "parent = None " + linesep
        else:
            Output_str += "parent = " + str(type(self.parent)) + " object" + linesep
        if self.simu is not None:
            tmp = self.simu.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "simu = " + tmp
        else:
            Output_str += "simu = None" + linesep + linesep
        Output_str += 'path_result = "' + str(self.path_result) + '"' + linesep
        if self.geo is not None:
            tmp = self.geo.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "geo = " + tmp
        else:
            Output_str += "geo = None" + linesep + linesep
        if self.elec is not None:
            tmp = self.elec.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "elec = " + tmp
        else:
            Output_str += "elec = None" + linesep + linesep
        if self.mag is not None:
            tmp = self.mag.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "mag = " + tmp
        else:
            Output_str += "mag = None" + linesep + linesep
        if self.struct is not None:
            tmp = self.struct.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "struct = " + tmp
        else:
            Output_str += "struct = None" + linesep + linesep
        if self.post is not None:
            tmp = self.post.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "post = " + tmp
        else:
            Output_str += "post = None" + linesep + linesep
        Output_str += 'logger_name = "' + str(self.logger_name) + '"' + linesep
        if self.force is not None:
            tmp = self.force.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "force = " + tmp
        else:
            Output_str += "force = None" + linesep + linesep
        if self.loss is not None:
            tmp = self.loss.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Output_str += "loss = " + tmp
        else:
            Output_str += "loss = None" + linesep + linesep
        return Output_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.simu != self.simu:
            return False
        if other.path_result != self.path_result:
            return False
        if other.geo != self.geo:
            return False
        if other.elec != self.elec:
            return False
        if other.mag != self.mag:
            return False
        if other.struct != self.struct:
            return False
        if other.post != self.post:
            return False
        if other.logger_name != self.logger_name:
            return False
        if other.force != self.force:
            return False
        if other.loss != self.loss:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (other.simu is None and self.simu is not None) or (
            other.simu is not None and self.simu is None
        ):
            diff_list.append(name + ".simu None mismatch")
        elif self.simu is not None:
            diff_list.extend(
                self.simu.compare(
                    other.simu,
                    name=name + ".simu",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._path_result != self._path_result:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._path_result)
                    + ", other="
                    + str(other._path_result)
                    + ")"
                )
                diff_list.append(name + ".path_result" + val_str)
            else:
                diff_list.append(name + ".path_result")
        if (other.geo is None and self.geo is not None) or (
            other.geo is not None and self.geo is None
        ):
            diff_list.append(name + ".geo None mismatch")
        elif self.geo is not None:
            diff_list.extend(
                self.geo.compare(
                    other.geo,
                    name=name + ".geo",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.elec is None and self.elec is not None) or (
            other.elec is not None and self.elec is None
        ):
            diff_list.append(name + ".elec None mismatch")
        elif self.elec is not None:
            diff_list.extend(
                self.elec.compare(
                    other.elec,
                    name=name + ".elec",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.mag is None and self.mag is not None) or (
            other.mag is not None and self.mag is None
        ):
            diff_list.append(name + ".mag None mismatch")
        elif self.mag is not None:
            diff_list.extend(
                self.mag.compare(
                    other.mag,
                    name=name + ".mag",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.struct is None and self.struct is not None) or (
            other.struct is not None and self.struct is None
        ):
            diff_list.append(name + ".struct None mismatch")
        elif self.struct is not None:
            diff_list.extend(
                self.struct.compare(
                    other.struct,
                    name=name + ".struct",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.post is None and self.post is not None) or (
            other.post is not None and self.post is None
        ):
            diff_list.append(name + ".post None mismatch")
        elif self.post is not None:
            diff_list.extend(
                self.post.compare(
                    other.post,
                    name=name + ".post",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._logger_name != self._logger_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._logger_name)
                    + ", other="
                    + str(other._logger_name)
                    + ")"
                )
                diff_list.append(name + ".logger_name" + val_str)
            else:
                diff_list.append(name + ".logger_name")
        if (other.force is None and self.force is not None) or (
            other.force is not None and self.force is None
        ):
            diff_list.append(name + ".force None mismatch")
        elif self.force is not None:
            diff_list.extend(
                self.force.compare(
                    other.force,
                    name=name + ".force",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.loss is None and self.loss is not None) or (
            other.loss is not None and self.loss is None
        ):
            diff_list.append(name + ".loss None mismatch")
        elif self.loss is not None:
            diff_list.extend(
                self.loss.compare(
                    other.loss,
                    name=name + ".loss",
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
        S += getsizeof(self.simu)
        S += getsizeof(self.path_result)
        S += getsizeof(self.geo)
        S += getsizeof(self.elec)
        S += getsizeof(self.mag)
        S += getsizeof(self.struct)
        S += getsizeof(self.post)
        S += getsizeof(self.logger_name)
        S += getsizeof(self.force)
        S += getsizeof(self.loss)
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

        Output_dict = dict()
        if self.simu is None:
            Output_dict["simu"] = None
        else:
            Output_dict["simu"] = self.simu.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        Output_dict["path_result"] = self.path_result
        if self.geo is None:
            Output_dict["geo"] = None
        else:
            Output_dict["geo"] = self.geo.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.elec is None:
            Output_dict["elec"] = None
        else:
            Output_dict["elec"] = self.elec.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.mag is None:
            Output_dict["mag"] = None
        else:
            Output_dict["mag"] = self.mag.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.struct is None:
            Output_dict["struct"] = None
        else:
            Output_dict["struct"] = self.struct.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.post is None:
            Output_dict["post"] = None
        else:
            Output_dict["post"] = self.post.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        Output_dict["logger_name"] = self.logger_name
        if self.force is None:
            Output_dict["force"] = None
        else:
            Output_dict["force"] = self.force.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        if self.loss is None:
            Output_dict["loss"] = None
        else:
            Output_dict["loss"] = self.loss.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs,
            )
        # The class name is added to the dict for deserialisation purpose
        Output_dict["__class__"] = "Output"
        return Output_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
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

        if self.simu is not None:
            self.simu._set_None()
        self.path_result = None
        if self.geo is not None:
            self.geo._set_None()
        if self.elec is not None:
            self.elec._set_None()
        if self.mag is not None:
            self.mag._set_None()
        if self.struct is not None:
            self.struct._set_None()
        if self.post is not None:
            self.post._set_None()
        self.logger_name = None
        if self.force is not None:
            self.force._set_None()
        if self.loss is not None:
            self.loss._set_None()

    def _get_simu(self):
        """getter of simu"""
        return self._simu

    def _set_simu(self, value):
        """setter of simu"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "simu")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Simulation = import_class("pyleecan.Classes", "Simulation", "simu")
            value = Simulation()
        check_var("simu", value, "Simulation")
        self._simu = value

        if self._simu is not None:
            self._simu.parent = self

    simu = property(
        fget=_get_simu,
        fset=_set_simu,
        doc="""Simulation object that generated the Output

        :Type: Simulation
        """,
    )

    def _get_path_result(self):
        """getter of path_result"""
        return self._path_result

    def _set_path_result(self, value):
        """setter of path_result"""
        check_var("path_result", value, "str")
        self._path_result = value

    path_result = property(
        fget=_get_path_result,
        fset=_set_path_result,
        doc="""Path to the folder to same the results

        :Type: str
        """,
    )

    def _get_geo(self):
        """getter of geo"""
        return self._geo

    def _set_geo(self, value):
        """setter of geo"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "geo")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutGeo = import_class("pyleecan.Classes", "OutGeo", "geo")
            value = OutGeo()
        check_var("geo", value, "OutGeo")
        self._geo = value

        if self._geo is not None:
            self._geo.parent = self

    geo = property(
        fget=_get_geo,
        fset=_set_geo,
        doc="""Geometry output

        :Type: OutGeo
        """,
    )

    def _get_elec(self):
        """getter of elec"""
        return self._elec

    def _set_elec(self, value):
        """setter of elec"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "elec")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutElec = import_class("pyleecan.Classes", "OutElec", "elec")
            value = OutElec()
        check_var("elec", value, "OutElec")
        self._elec = value

        if self._elec is not None:
            self._elec.parent = self

    elec = property(
        fget=_get_elec,
        fset=_set_elec,
        doc="""Electrical module output

        :Type: OutElec
        """,
    )

    def _get_mag(self):
        """getter of mag"""
        return self._mag

    def _set_mag(self, value):
        """setter of mag"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "mag")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutMag = import_class("pyleecan.Classes", "OutMag", "mag")
            value = OutMag()
        check_var("mag", value, "OutMag")
        self._mag = value

        if self._mag is not None:
            self._mag.parent = self

    mag = property(
        fget=_get_mag,
        fset=_set_mag,
        doc="""Magnetic module output

        :Type: OutMag
        """,
    )

    def _get_struct(self):
        """getter of struct"""
        return self._struct

    def _set_struct(self, value):
        """setter of struct"""
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
                "pyleecan.Classes", value.get("__class__"), "struct"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutStruct = import_class("pyleecan.Classes", "OutStruct", "struct")
            value = OutStruct()
        check_var("struct", value, "OutStruct")
        self._struct = value

        if self._struct is not None:
            self._struct.parent = self

    struct = property(
        fget=_get_struct,
        fset=_set_struct,
        doc="""Structural module output

        :Type: OutStruct
        """,
    )

    def _get_post(self):
        """getter of post"""
        return self._post

    def _set_post(self, value):
        """setter of post"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "post")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutPost = import_class("pyleecan.Classes", "OutPost", "post")
            value = OutPost()
        check_var("post", value, "OutPost")
        self._post = value

        if self._post is not None:
            self._post.parent = self

    post = property(
        fget=_get_post,
        fset=_set_post,
        doc="""Post-Processing settings

        :Type: OutPost
        """,
    )

    def _get_logger_name(self):
        """getter of logger_name"""
        return self._logger_name

    def _set_logger_name(self, value):
        """setter of logger_name"""
        check_var("logger_name", value, "str")
        self._logger_name = value

    logger_name = property(
        fget=_get_logger_name,
        fset=_set_logger_name,
        doc="""Name of the logger to use

        :Type: str
        """,
    )

    def _get_force(self):
        """getter of force"""
        return self._force

    def _set_force(self, value):
        """setter of force"""
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
                "pyleecan.Classes", value.get("__class__"), "force"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutForce = import_class("pyleecan.Classes", "OutForce", "force")
            value = OutForce()
        check_var("force", value, "OutForce")
        self._force = value

        if self._force is not None:
            self._force.parent = self

    force = property(
        fget=_get_force,
        fset=_set_force,
        doc="""Force module output

        :Type: OutForce
        """,
    )

    def _get_loss(self):
        """getter of loss"""
        return self._loss

    def _set_loss(self, value):
        """setter of loss"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "loss")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OutLoss = import_class("pyleecan.Classes", "OutLoss", "loss")
            value = OutLoss()
        check_var("loss", value, "OutLoss")
        self._loss = value

        if self._loss is not None:
            self._loss.parent = self

    loss = property(
        fget=_get_loss,
        fset=_set_loss,
        doc="""Loss module output

        :Type: OutLoss
        """,
    )

    class GetOutError(Exception):
        """Raised when an output can't be returned"""

        pass


GetOutError = Output.GetOutError
