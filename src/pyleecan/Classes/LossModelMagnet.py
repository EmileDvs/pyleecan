# File generated according to Generator/ClassesRef/Loss/LossModelMagnet.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Loss/LossModelMagnet"""

import numpy as np

from pyleecan.Classes.HoleM50 import HoleM50
from pyleecan.Classes.HoleM51 import HoleM51
from pyleecan.Classes.HoleM52 import HoleM52
from pyleecan.Classes.HoleM53 import HoleM53
from pyleecan.Classes.HoleM57 import HoleM57
from pyleecan.Classes.HoleM58 import HoleM58
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.LamSlotMag import LamSlotMag
from pyleecan.Classes.LossModel import LossModel
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class LossModelMagnet(LossModel):
    """Magnet Loss Model Class"""

    VERSION = 1

    # cf Methods.Loss.LossModelMagnet.comp_loss
    def comp_loss(self):
        """Calculate eddy-current losses in rotor permanent magnets assuming power density
        is given by (cf. https://www.femm.info/wiki/SPMLoss):

            Pmag = Jm^2/sigma_m with Jm = -sigma_m*1j*2pi*f*Az + Jc where Jc=<Jm> on the magnet surface

        Parameters
        ----------
        self: LossModelMagnet
            a LossModelMagnet object

        Returns
        -------
        Pmagnet_density : ndarray
            Magnet loss density function of frequency and elements [W/m3]
        freqs: ndarray
            frequency vector [Hz]
        """

        if self.parent.parent.parent is None:
            raise Exception("Cannot calculate core losses if simu is not in an Output")
        else:
            output = self.parent.parent.parent

        machine = output.simu.machine

        per_a = output.geo.per_a
        if output.geo.is_antiper_a:
            per_a *= 2

        if isinstance(machine.rotor, LamSlotMag):
            magnet = machine.rotor.magnet
            slot = machine.rotor.slot
            if hasattr(slot, "Hmag"):
                Hmag = slot.Hmag
            else:
                Hmag = np.sqrt(slot.comp_surface_active())
            if hasattr(slot, "Wmag"):
                Wmag = slot.Wmag
            else:
                Wmag = np.sqrt(slot.comp_surface_active())

        elif isinstance(machine.rotor, LamHole):
            hole0 = machine.rotor.hole[0]
            magnet = hole0.get_magnet_dict()["magnet_0"]
            if isinstance(hole0, HoleM50):
                Hmag = hole0.H3
                Wmag = hole0.W4
            elif isinstance(hole0, (HoleM51, HoleM53, HoleM57, HoleM58)):
                Hmag = hole0.H2
                if isinstance(hole0, HoleM51):
                    Wmag = (hole0.W3 + hole0.W5 + hole0.W7) / 3
                elif isinstance(hole0, HoleM53):
                    Wmag = hole0.W3
                elif isinstance(hole0, HoleM57):
                    Wmag = hole0.W4
                elif isinstance(hole0, HoleM58):
                    Wmag = hole0.W1
            elif isinstance(hole0, HoleM52):
                Hmag = hole0.H1
                Wmag = hole0.W0
            else:  # HoleUD
                Hmag = np.sqrt(hole0.comp_surface_magnet_id(0))
                Wmag = Hmag
        else:
            raise Exception(
                "Cannot calculate magnet losses for rotor lamination other than LamSlotMag or LamHole"
            )

        # Get rotor length
        L1 = machine.rotor.L1

        # Calculate segmentation coefficient from:
        # "Effect of Eddy-Current Loss Reduction by Magnet Segmentation in Synchronous Motors With Concentrated Windings"
        # Katsumi Yamazaki, Member, IEEE, and Yu Fukushima, Equation (9)
        if (
            magnet.Lmag is None
            or magnet.Nseg is None
            or Wmag is None
            or magnet.Nseg == 1
        ):
            kseg = 1
        else:
            Lmag = magnet.Lmag
            Nseg = magnet.Nseg
            kseg = ((Lmag + Wmag) / (Lmag * Nseg + Wmag)) ** 2

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag is None:
            raise Exception("Cannot calculate magnet losses if OutMag is None")

        if output.mag.meshsolution is None:
            raise Exception(
                "Cannot calculate magnet losses if OutMag.meshsolution is None"
            )
        else:
            meshsol = output.mag.meshsolution

        group_list = list(meshsol.group.keys())

        if self.group not in group_list:
            raise Exception("Cannot calculate magnet losses for group=" + self.group)

        # Extract the solution
        solution_A = meshsol["A_z^{element}"]

        if solution_A.type_element != "triangle":
            raise ValueError(
                "Cannot calculate magnet losses if A_z calculated on element center is not in meshsolution"
            )

        # Get magnetic vector potential over time and for each element center in current group
        Az_dt = solution_A.field
        axes_list = Az_dt.get_axes()
        Time_orig = axes_list[0]
        Time = Time_orig.copy()

        # Check Time axis periodicity in function of group
        is_change_Time = False
        if "rotor" in self.group:
            if "antiperiod" in Time_orig.symmetries:
                Time.symmetries = {"period": Time_orig.symmetries["antiperiod"]}
                is_change_Time = True
        if is_change_Time:
            Az_dt.axes[0] = Time

        # Get all element surfaces
        Se = meshsol.mesh.get_element_area()

        # Get list of element indices for each magnet
        list_Imag = list()
        ind_list = list()
        for key in meshsol.group:
            if self.group in key and key != self.group:
                ind = int(key.split("_")[-1])
                ind_list.append(ind)
                list_Imag.append(meshsol.group[key])
        ind_all = meshsol.group[self.group]

        # Calculate induced current density and loss density
        jj = 0
        for ii, kmag in enumerate(list_Imag):
            Se_mag = Se[kmag]

            # derivation in frequency domain
            Az_df = Az_dt.get_along("freqs", "indice" + str(kmag), "z=mean")
            if ii == 0:
                freqs = Az_df["freqs"]
                w = 2 * np.pi * freqs[:, None]
                sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.parent.Trot)
                # if self.type_skin_effect:
                #     # Get magnet conductivity including skin effect
                #     magnet_cond = CondType21(Hbar=Hmag, Wbar=1, cond_mat=magnet.mat_type)
                #     kr_skin = magnet_cond.comp_skin_effect_resistance(
                #         freqs, T_op=self.parent.Trot, b=1, zt=1
                #     )
                #     kr_skin[np.isnan(kr_skin)] = 1
                #     sigma_m = sigma_m / kr_skin[:, None]
                Pmagnet_density = np.zeros((freqs.size, len(ind_all)))
            Az_fft = Az_df["A_z^{element}"]
            Az_mean = np.matmul(Az_fft, Se_mag)[:, None] / np.sum(Se_mag)
            Jm_fft = -1j * sigma_m * w * (Az_fft - Az_mean)
            Pmagnet_density[:, jj : (jj + len(kmag))] = (
                0.5 * kseg * np.abs(Jm_fft) ** 2 / sigma_m
            )
            jj += len(kmag)

            # # # derivation in time domain
            # dAz_dt = Az_dt.get_data_along("time=derivate", "indice" + str(kmag), "z[0]")
            # dAz_df = dAz_dt.get_along("freqs", "indice", "z[0]")
            # dAz_fft = dAz_df["A_z"]
            # if ii == 0:
            #     freqs = dAz_df["freqs"]
            #     w = 2 * pi * freqs[:, None]
            #     sigma_m = magnet.mat_type.elec.get_conductivity(T_op=self.Trot)
            #     if is_skin_effect:
            #         # Get magnet conductivity including skin effect
            #         magnet_cond = CondType21(Hbar=Hmag, Wbar=1, cond_mat=magnet.mat_type)
            #         kr_skin = magnet_cond.comp_skin_effect_resistance(
            #             freqs, T_op=self.Trot, b=1, zt=1
            #         )
            #         kr_skin[np.isnan(kr_skin)] = 1
            #         sigma_m = sigma_m / kr_skin[:, None]
            #     Pmagnet_density = np.zeros((freqs.size, len(ind_all)))
            # Jm_fft0 = sigma_m * (
            #     -dAz_fft + matmul(dAz_fft, Se_mag)[:, None] / np_sum(Se_mag)
            # )

            # # # Plot
            # Az_df0 = Az_dt.get_data_along("freqs", "indice" + str(kmag), "z[0]")
            # dAz_df0 = Az_df0.copy()
            # dAz_df0.values *= 1j * w[:, :, None]
            # dAz_df0.unit = "Wb/ms"
            # dAz_df0.plot_2D_Data(
            #     "freqs", "indice[0]", data_list=[dAz_dt], legend_list=["df", "dt"]
            # )
            # dAz_df0.plot_2D_Data(
            #     "time", "indice[0]", data_list=[dAz_dt], legend_list=["df", "dt"]
            # )
            # from SciDataTool import DataFreq

            # Jm_df = DataFreq(
            #     name="Current density",
            #     symbol="J_m",
            #     unit="A/m^2",
            #     values=Jm_fft,
            #     axes=Az_df0.axes,
            # )
            # Jm_df0 = DataFreq(
            #     name="Current density",
            #     symbol="J_m",
            #     unit="A/m^2",
            #     values=Jm_fft0,
            #     axes=Az_df0.axes,
            # )
            # Jm_df.plot_2D_Data(
            #     "time", "indice[0]", data_list=[Jm_df0], legend_list=["df", "dt"]
            # )
            # Jm_df.plot_2D_Data(
            #     "freqs", "indice[0]", data_list=[Jm_df0], legend_list=["df", "dt"]
            # )

        if is_change_Time:
            # Change periodicity back to original periodicity
            Az_dt.axes[0] = Time_orig

        # Get frequency orders
        n = freqs / felec
        # Integrate loss density over group volume
        I0 = n != 0
        Af = np.zeros(w.size)
        Af[I0] = (
            L1
            * per_a
            * np.matmul(Pmagnet_density[I0, :] / freqs[I0, None] ** 2, Se[ind_all])
        )
        # Sum over orders
        A = np.sum(Af * n**2)
        self.coeff_dict = {"2": A}

        return Pmagnet_density, freqs

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        name="",
        group="",
        is_show_fig=False,
        coeff_dict=None,
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
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "group" in list(init_dict.keys()):
                group = init_dict["group"]
            if "is_show_fig" in list(init_dict.keys()):
                is_show_fig = init_dict["is_show_fig"]
            if "coeff_dict" in list(init_dict.keys()):
                coeff_dict = init_dict["coeff_dict"]
        # Set the properties (value check and convertion are done in setter)
        # Call LossModel init
        super(LossModelMagnet, self).__init__(
            name=name, group=group, is_show_fig=is_show_fig, coeff_dict=coeff_dict
        )
        # The class is frozen (in LossModel init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LossModelMagnet_str = ""
        # Get the properties inherited from LossModel
        LossModelMagnet_str += super(LossModelMagnet, self).__str__()
        return LossModelMagnet_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LossModel
        if not super(LossModelMagnet, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LossModel
        diff_list.extend(
            super(LossModelMagnet, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from LossModel
        S += super(LossModelMagnet, self).__sizeof__()
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

        # Get the properties inherited from LossModel
        LossModelMagnet_dict = super(LossModelMagnet, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LossModelMagnet_dict["__class__"] = "LossModelMagnet"
        return LossModelMagnet_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        name_val = self.name
        group_val = self.group
        is_show_fig_val = self.is_show_fig
        if self.coeff_dict is None:
            coeff_dict_val = None
        else:
            coeff_dict_val = self.coeff_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            name=name_val,
            group=group_val,
            is_show_fig=is_show_fig_val,
            coeff_dict=coeff_dict_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from LossModel
        super(LossModelMagnet, self)._set_None()
