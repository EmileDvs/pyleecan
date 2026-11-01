# File generated according to Generator/ClassesRef/Output/LUTdq.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Output/LUTdq"""

from os import linesep
from sys import getsizeof

import numpy as np
import scipy.interpolate as scp_int

from pyleecan.Classes._check import check_var
from pyleecan.Classes.EEC_PMSM import EEC_PMSM
from pyleecan.Classes.Electrical import Electrical
from pyleecan.Classes.LUT import LUT
from pyleecan.Functions.Electrical.dqh_transformation import n2dqh_DataTime
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save


class LUTdq(LUT):
    """Look Up Table class for dq OP matrix"""

    VERSION = 1

    # cf Methods.Output.LUTdq.get_index_open_circuit
    def get_index_open_circuit(self):
        """Get index of open circuit point in output list

        Parameters
        ----------
        self : LUTdq
            a LUTdq object

        Returns
        -------
        index : int
            Index of open circuit point in output list

        """

        # Find Id=Iq=0
        OP_list = self.get_OP_array("Id", "Iq").tolist()
        if [0, 0] in OP_list:
            index = OP_list.index([0, 0])
        else:
            index = None

        return index

    # cf Methods.Output.LUTdq.get_L_dqh
    def get_L_dqh(self, Id, Iq, L_endwinding=0, Phi_dqh=None):
        """Get the total dqh inductance
        TODO: calculate end-winding inductance from machine

        Parameters
        ----------
        self : LUTdq
            a LUTdq object
        Id : float
            current Id
        Iq : float
            current Iq
        L_endwinding : float
            end winding inductance provided by user
        Phi_dqh: ndarray
            Stator winding dqh flux

        Returns
        ----------
        Ldqh : ndarray
            ddqh inductance
        """

        Lmdqh = self.get_Lm_dqh(Id=Id, Iq=Iq, Phi_dqh=Phi_dqh)

        if Lmdqh is None:
            return None
        else:
            return Lmdqh + L_endwinding

    # cf Methods.Output.LUTdq.get_Lm_dqh
    def get_Lm_dqh(self, Id, Iq, Phi_dqh=None):
        """Get the magnetizing dqh inductance

        Parameters
        ----------
        self : LUTdq
            a LUTdq object
        Id : float
            current Id
        Iq : float
            current Iq
        Phi_dqh: ndarray
            Stator winding dqh flux

        Returns
        ----------
        Lmdqh : ndarray
            magnetizing dqh inductance
        """

        if Phi_dqh is None:
            Phi_dqh = self.interp_Phi_dqh(Id=Id, Iq=Iq)

        # Get dqh flux linkage (without currents, only due to PM)
        Phi_dqh_mag = self.get_Phi_dqh_mag_mean()

        if Phi_dqh_mag is not None:
            # Init dqh current
            if np.isscalar(Id) and np.isscalar(Iq):
                I_dqh = np.zeros(3)
            else:
                I_dqh = np.zeros((3, Id.size))
                Phi_dqh_mag = Phi_dqh_mag[:, None]
            I_dqh[0] = Id
            I_dqh[1] = Iq
            I_dqh[2] = 1

            # Divide flux by current to get inductance
            Lmdqh = (Phi_dqh - Phi_dqh_mag) / I_dqh
        else:
            Lmdqh = None

        return Lmdqh

    # cf Methods.Output.LUTdq.get_Phi_dqh_mag
    def get_Phi_dqh_mag(self):
        """Get magnet flux linkage over time in DQH frame

        Parameters
        ----------
        self : LUTdq
            a LUTdq object

        Returns
        ----------
        Phi_dqh_mag : DataND
            magnets flux linkage in dqh frame (Nt_tot, 3)
        """

        if self.Phi_dqh_mag is None:
            # Find Id=Iq=0
            ii = self.get_index_open_circuit()

            if ii is not None:
                stator_label = self.simu.machine.stator.get_label()

                phase_dir = self.output_list[ii].elec.phase_dir

                # Integrate stator winding flux contained in LUT over z
                Phi_wind0 = (
                    self.output_list[ii]
                    .mag.Phi_wind_slice[stator_label]
                    .get_data_along("time", "phase", "z=integrate")
                )

                # dqh transform
                Phi_dqh_mag = n2dqh_DataTime(
                    Phi_wind0,
                    is_dqh_rms=True,
                    phase_dir=phase_dir,
                )

                # Store for next call
                self.Phi_dqh_mag = Phi_dqh_mag

        return self.Phi_dqh_mag

    # cf Methods.Output.LUTdq.get_Phi_dqh_mag_mean
    def get_Phi_dqh_mag_mean(self):
        """Get the mean magnets flux linkage in DQH frame

        Parameters
        ----------
        self : LUTdq
            a LUTdq object

        Returns
        ----------
        Phi_dqh_mag_mean : ndarray
            mean magnets flux linkage in dqh frame (3,)
        """

        eec = self.get_eec()

        if eec is not None and eec.Phid_mag is not None and eec.Phiq_mag is not None:
            Phi_dqh_mag_mean = np.array([eec.Phid_mag, eec.Phiq_mag, 0])
        else:
            # Get stator winding flux due to magnets
            Phi_dqh_mag = self.get_Phi_dqh_mag()

            if Phi_dqh_mag is not None:
                # Get mean value
                Phi_dqh_mag_mean = Phi_dqh_mag.get_along("time=mean", "phase")[
                    Phi_dqh_mag.symbol
                ]
                # Store in eec for further use
                if eec is None:
                    eec = EEC_PMSM()
                    if self.simu.elec is None:
                        self.simu.elec = Electrical()
                    self.simu.elec.eec = eec
                eec.Phid_mag = float(Phi_dqh_mag_mean[0])
                eec.Phiq_mag = float(Phi_dqh_mag_mean[1])

            else:
                Phi_dqh_mag_mean = None

        return Phi_dqh_mag_mean

    # cf Methods.Output.LUTdq.get_Phi_dqh_mean
    def get_Phi_dqh_mean(self):
        """Get the mean value of stator flux along dqh axes

        Parameters
        ----------
        self : LUTdq
            a LUTdq object

        Returns
        ----------
        Phi_dqh_mean : ndarray
            mean flux linkage in dqh frame (N_dq, 3)
        """

        if self.Phi_dqh_mean is None:
            N_OP = len(self.output_list)

            Phi_dqh_mean = np.zeros((N_OP, 3))

            stator_label = self.simu.machine.stator.get_label()

            phase_dir = self.output_list[0].elec.phase_dir

            for ii in range(N_OP):
                eec_i = self.output_list[ii].elec.eec

                if (
                    eec_i is not None
                    and eec_i.Phid is not None
                    and eec_i.Phiq is not None
                ):
                    # Get values from eec
                    Phi_dqh_mean[ii, :] = np.array([eec_i.Phid, eec_i.Phiq, 0])

                else:
                    # Integrate stator winding flux contained in LUT over z
                    Phi_wind = (
                        self.output_list[ii]
                        .mag.Phi_wind_slice[stator_label]
                        .get_data_along("time", "phase", "z=integrate")
                    )

                    # dqh transform
                    Phi_dqh = n2dqh_DataTime(
                        Phi_wind,
                        is_dqh_rms=True,
                        phase_dir=phase_dir,
                    )
                    # mean over time axis
                    Phi_dqh_mean[ii, :] = Phi_dqh.get_along("time=mean", "phase")[
                        Phi_dqh.symbol
                    ]

                    # Store values in eec for further use
                    if eec_i is None:
                        eec_i = EEC_PMSM()
                        self.output_list[ii].elec.eec = eec_i
                    eec_i.Phid = float(Phi_dqh_mean[ii, 0])
                    eec_i.Phiq = float(Phi_dqh_mean[ii, 1])

            # Store for next call
            self.Phi_dqh_mean = Phi_dqh_mean

        return self.Phi_dqh_mean

    # cf Methods.Output.LUTdq.interp_Phi_dqh
    def interp_Phi_dqh(self, Id, Iq):
        """Interpolate stator winding dqh flux in dq plane

        Parameters
        ----------
        self : LUTdq
            a LUTdq object
        Id : float or ndarray
            current Id
        Iq : float or ndarray
            current Iq

        Returns
        ----------
        Phi_dqh : float or ndarray
            interpolated flux in dqh frame (3)
        """

        # Calculate average value of dqh flux linkage
        Phi_dqh_mean = self.get_Phi_dqh_mean()

        # Get unique Id, Iq sorted in ascending order
        OP_matrix = self.get_OP_array("N0", "Id", "Iq")
        XId, jd = np.unique(OP_matrix[:, 1], return_inverse=True)
        XIq, jq = np.unique(OP_matrix[:, 2], return_inverse=True)
        nd, nq = XId.size, XIq.size

        Phi_dqh_mean_reg = np.zeros((nd, nq, 2))
        if nd * nq == OP_matrix.shape[0]:
            # sort flux linkage matrix and reshape to (nd, nq, 2)
            is_rect_interp = True
            for ii, (m, n) in enumerate(zip(jd, jq)):
                Phi_dqh_mean_reg[m, n, :] = Phi_dqh_mean[ii, 0:2]
        elif nd + nq - 1 == OP_matrix.shape[0]:
            # Rebuild 2D grid from xId and xIq
            is_rect_interp = True
            Phi_dqh_mag = self.get_Phi_dqh_mag_mean()
            for m, x in enumerate(XId):
                for n, y in enumerate(XIq):
                    # Find indice of current Id value in OP_matrix
                    ii = np.where(OP_matrix[:, 1] == x)[0]
                    # Find indice of current Iq value in OP_matrix
                    jj = np.where(OP_matrix[:, 2] == y)[0]
                    # check if (Id, Iq) is in OP_matrix
                    kk = np.intersect1d(ii, jj)
                    if kk.size > 0:
                        # take values directly from Phi_dqh_mean if (Id, Iq) is in OP_matrix
                        Phi_dqh_mean_reg[m, n, :] = Phi_dqh_mean[kk, 0:2]
                    else:
                        # Sum flux values for (Id, Iq): Phi_dq(Id, Iq) = Phi_dq(Id, 0) + Phi_dq(0, Iq)
                        Phi_dqh_mean_reg[m, n, :] = (
                            Phi_dqh_mean[ii, :2]
                            + Phi_dqh_mean[jj, :2]
                            - Phi_dqh_mag[:2]
                        )
        else:
            is_rect_interp = False

        if nd == 1:
            # 1D interpolation along q axis
            Phi_dqh_interp = scp_int.interp1d(
                XIq, Phi_dqh_mean_reg, kind="linear", axis=1
            )
        elif nq == 1:
            # 1D interpolation along d axis
            Phi_dqh_interp = scp_int.interp1d(
                XId, Phi_dqh_mean_reg, kind="linear", axis=0
            )
        elif is_rect_interp:
            # 2D regular grid interpolation
            Phi_dqh_interp = scp_int.RegularGridInterpolator(
                (XId, XIq), Phi_dqh_mean_reg, method="linear"
            )
        else:
            # 2D scattered interpolation
            Phi_dqh_interp = scp_int.LinearNDInterpolator(
                (OP_matrix[:, 1], OP_matrix[:, 2]), Phi_dqh_mean[:, 0:2]
            )

        # Init dqh flux linkage
        if np.isscalar(Id) and np.isscalar(Iq):
            n_OP = 1
        else:
            n_OP = Id.size
        Phi_dqh = np.zeros((3, n_OP))

        if nd == 1:
            Phi_dqh[0:2, :] = np.squeeze(Phi_dqh_interp(Iq)).T
        elif nq == 1:
            Phi_dqh[0:2, :] = np.squeeze(Phi_dqh_interp(Id)).T
        else:
            Phid_dqh_val = Phi_dqh_interp((Id, Iq))
            # Interpolate Phid and Phiq, Phih is enforced to 0
            if n_OP == 1:
                Phi_dqh[0:2, :] = Phid_dqh_val[:, None]
            else:
                Phi_dqh[0:2, :] = Phid_dqh_val.T

        return Phi_dqh

    # cf Methods.Output.LUTdq.interp_Ploss_dqh
    def interp_Ploss_dqh(self, Id, Iq, N0, exclude_models=[]):
        """Interpolate losses in function of Id and Iq and for given speed
        Meant to be used with SIPMSM/IPMSM machine with LossFEA (to have the correct loss models name)

        Parameters
        ----------
        self : LUTdq
            a LUTdq object
        Id : float or ndarray
            current Id
        Iq : float or ndarray
            current Iq
        N0: float
            rotation speed [rpm]
        exclude_models: list of strings
            list of LossModel names to exclude from the interpolation

        Returns
        ----------
        Ploss_dqh : float or ndarray
            interpolated losses function of dq currents (N_OP, 5)
            - 1st column : Joule losses
            - 2nd column : stator core losses
            - 3rd column : magnet losses
            - 4th column : rotor core losses
            - 5th column : proximity losses
        """

        # Name of the losses model to interpolate (in order)
        name_list = ["joule", "stator core", "magnets", "rotor core", "proximity"]
        # Check that all the losses are available
        if self.output_list is None or len(self.output_list) == 0:
            raise Exception(
                "Error, interpolation requires output_list, check is_keep_all_output"
            )
        out1 = self.output_list[0]
        for name in name_list:
            if name not in out1.loss.loss_dict.keys():
                raise Exception(
                    "Error "
                    + name
                    + " is missing in "
                    + str(out1.loss.loss_dict.keys())
                )

        p = self.simu.machine.get_pole_pair_number()

        felec = N0 / 60 * p

        Ploss_dqh = np.zeros(
            (len(self.output_list), len(self.output_list[0].loss.loss_dict))
        )
        for ii, out in enumerate(self.output_list):
            for kk, loss_name in enumerate(name_list):
                loss = out.loss.loss_dict[loss_name]
                if loss.loss_model not in exclude_models:
                    Ploss_dqh[ii, kk] = loss.get_loss_scalar(felec)

        # Get unique Id, Iq sorted in ascending order
        OP_matrix = self.get_OP_array("N0", "Id", "Iq")
        XId, jd = np.unique(OP_matrix[:, 1], return_inverse=True)
        XIq, jq = np.unique(OP_matrix[:, 2], return_inverse=True)
        nd, nq = XId.size, XIq.size

        Ploss_dqh_mat = np.zeros((nd, nq, 5))
        # Perform 2D interpolation
        if nd * nq == OP_matrix.shape[0]:
            # sort flux linkage matrix and reshape to (nd, nq, 2)
            is_rect_interp = True
            for ii, (m, n) in enumerate(zip(jd, jq)):
                Ploss_dqh_mat[m, n, :] = Ploss_dqh[ii, :]
        elif nd + nq - 1 == OP_matrix.shape[0]:
            # Rebuild 2D grid from xId and xIq
            is_rect_interp = True
            # Find Id=Iq=0
            i0 = self.get_index_open_circuit()
            Ploss_dqh_mag = Ploss_dqh[i0, :]
            for m, x in enumerate(XId):
                for n, y in enumerate(XIq):
                    # Find indice of current Id value in OP_matrix
                    ii = np.where(OP_matrix[:, 1] == x)[0]
                    # Find indice of current Iq value in OP_matrix
                    jj = np.where(OP_matrix[:, 2] == y)[0]
                    # check if (Id, Iq) is in OP_matrix
                    kk = np.intersect1d(ii, jj)
                    if kk.size > 0:
                        # take values directly from Phi_dqh_mean if (Id, Iq) is in OP_matrix
                        Ploss_dqh_mat[m, n, :] = Ploss_dqh[kk, :]
                    else:
                        # Sum flux values for (Id, Iq): Phi_dq(Id, Iq) = Phi_dq(Id, 0) + Phi_dq(0, Iq)
                        Ploss_dqh_mat[m, n, :] = (
                            Ploss_dqh[ii, :] + Ploss_dqh[jj, :] - Ploss_dqh_mag
                        )

        else:
            is_rect_interp = False

        if nd == 1:
            # 1D interpolation along q axis
            Ploss_dqh_interp = scp_int.interp1d(
                XIq, Ploss_dqh_mat, kind="linear", axis=1
            )
        elif nq == 1:
            # 1D interpolation along d axis
            Ploss_dqh_interp = scp_int.interp1d(
                XId, Ploss_dqh_mat, kind="linear", axis=0
            )
        elif is_rect_interp:
            # regular grid interpolation
            Ploss_dqh_interp = scp_int.RegularGridInterpolator(
                (XId, XIq), Ploss_dqh_mat, method="linear"
            )
        else:
            # scattered interpolation
            # not working since LinearNDInterpolator is not of same class as RegularGridInterpolator
            Ploss_dqh_interp = scp_int.LinearNDInterpolator(
                (OP_matrix[:, 1], OP_matrix[:, 2]), Ploss_dqh
            )

        # Interpolate losses function of dq currents
        if nd == 1:
            Ploss_dqh = np.squeeze(Ploss_dqh_interp(Iq))
        elif nq == 1:
            Ploss_dqh = np.squeeze(Ploss_dqh_interp(Id))
        else:
            if np.isscalar(Id) and np.isscalar(Iq):
                Ploss_dqh = Ploss_dqh_interp((Id, Iq))[:, None]
            else:
                Ploss_dqh = Ploss_dqh_interp((Id, Iq))

        return Ploss_dqh

    # cf Methods.Output.LUTdq.interp_Tem_rip_dqh
    def interp_Tem_rip_dqh(self, Id, Iq):
        """Interpolate torque ripple in dq plane

        Parameters
        ----------
        self : LUTdq
            a LUTdq object
        Id : float or ndarray
            current Id
        Iq : float or ndarray
            current Iq

        Returns
        ----------
        Tem_rip_pp : float or ndarray
            interpolated flux in dqh frame (3)
        """

        if self.output_list[0].mag.Tem_rip_pp is None:
            return None

        # Get torque ripple for each operating point
        Tem_rip_pp_dqh = np.array([out.mag.Tem_rip_pp for out in self.output_list])

        # Get unique Id, Iq sorted in ascending order
        OP_matrix = self.get_OP_array("N0", "Id", "Iq")
        XId, jd = np.unique(OP_matrix[:, 1], return_inverse=True)
        XIq, jq = np.unique(OP_matrix[:, 2], return_inverse=True)
        nd, nq = XId.size, XIq.size

        Tem_rip_pp_dqh_reg = np.zeros((nd, nq))
        if nd * nq == OP_matrix.shape[0]:
            # sort flux linkage matrix and reshape to (nd, nq, 2)
            is_rect_interp = True
            for ii, (m, n) in enumerate(zip(jd, jq)):
                Tem_rip_pp_dqh_reg[m, n] = Tem_rip_pp_dqh[ii]
        else:
            is_rect_interp = False

        if nd == 1:
            # 1D interpolation along q axis
            Tem_rip_interp = scp_int.interp1d(
                XIq, Tem_rip_pp_dqh_reg, kind="linear", axis=1
            )
        elif nq == 1:
            # 1D interpolation along d axis
            Tem_rip_interp = scp_int.interp1d(
                XId, Tem_rip_pp_dqh_reg, kind="linear", axis=0
            )
        elif is_rect_interp:
            # 2D regular grid interpolation
            Tem_rip_interp = scp_int.RegularGridInterpolator(
                (XId, XIq), Tem_rip_pp_dqh_reg, method="linear"
            )
        else:
            # 2D scattered interpolation
            # not working since LinearNDInterpolator is not of same class as RegularGridInterpolator
            Tem_rip_interp = scp_int.LinearNDInterpolator(
                (OP_matrix[:, 1], OP_matrix[:, 2]), Tem_rip_pp_dqh
            )

        # Init dqh flux linkage
        if np.isscalar(Id) and np.isscalar(Iq):
            n_OP = 1
        else:
            n_OP = Id.size
        Tem_rip_pp = np.zeros(n_OP)

        if nd == 1:
            Tem_rip_pp = Tem_rip_interp(Iq)
        elif nq == 1:
            Tem_rip_pp = Tem_rip_interp(Id)
        else:
            Tem_rip_pp = Tem_rip_interp((Id, Iq))

        return Tem_rip_pp

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Phi_dqh_mean=None,
        Phi_dqh_mag=None,
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
            if "Phi_dqh_mean" in list(init_dict.keys()):
                Phi_dqh_mean = init_dict["Phi_dqh_mean"]
            if "Phi_dqh_mag" in list(init_dict.keys()):
                Phi_dqh_mag = init_dict["Phi_dqh_mag"]
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
        self.Phi_dqh_mean = Phi_dqh_mean
        self.Phi_dqh_mag = Phi_dqh_mag
        # Call LUT init
        super(LUTdq, self).__init__(
            paramexplorer_list=paramexplorer_list,
            output_list=output_list,
            xoutput_dict=xoutput_dict,
            nb_simu=nb_simu,
            xoutput_ref=xoutput_ref,
            xoutput_ref_index=xoutput_ref_index,
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
        # The class is frozen (in LUT init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LUTdq_str = ""
        # Get the properties inherited from LUT
        LUTdq_str += super(LUTdq, self).__str__()
        LUTdq_str += (
            "Phi_dqh_mean = "
            + linesep
            + str(self.Phi_dqh_mean).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        if self.Phi_dqh_mag is not None:
            tmp = (
                self.Phi_dqh_mag.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            LUTdq_str += "Phi_dqh_mag = " + tmp
        else:
            LUTdq_str += "Phi_dqh_mag = None" + linesep + linesep
        return LUTdq_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from LUT
        if not super(LUTdq, self).__eq__(other):
            return False
        if not np.array_equal(other.Phi_dqh_mean, self.Phi_dqh_mean):
            return False
        if other.Phi_dqh_mag != self.Phi_dqh_mag:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from LUT
        diff_list.extend(
            super(LUTdq, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if not np.array_equal(other.Phi_dqh_mean, self.Phi_dqh_mean):
            diff_list.append(name + ".Phi_dqh_mean")
        if (other.Phi_dqh_mag is None and self.Phi_dqh_mag is not None) or (
            other.Phi_dqh_mag is not None and self.Phi_dqh_mag is None
        ):
            diff_list.append(name + ".Phi_dqh_mag None mismatch")
        elif self.Phi_dqh_mag is not None:
            diff_list.extend(
                self.Phi_dqh_mag.compare(
                    other.Phi_dqh_mag,
                    name=name + ".Phi_dqh_mag",
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

        # Get size of the properties inherited from LUT
        S += super(LUTdq, self).__sizeof__()
        S += getsizeof(self.Phi_dqh_mean)
        S += getsizeof(self.Phi_dqh_mag)
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

        # Get the properties inherited from LUT
        LUTdq_dict = super(LUTdq, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.Phi_dqh_mean is None:
            LUTdq_dict["Phi_dqh_mean"] = None
        else:
            if type_handle_ndarray == 0:
                LUTdq_dict["Phi_dqh_mean"] = self.Phi_dqh_mean.tolist()
            elif type_handle_ndarray == 1:
                LUTdq_dict["Phi_dqh_mean"] = self.Phi_dqh_mean.copy()
            elif type_handle_ndarray == 2:
                LUTdq_dict["Phi_dqh_mean"] = self.Phi_dqh_mean
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        if self.Phi_dqh_mag is None:
            LUTdq_dict["Phi_dqh_mag"] = None
        else:
            LUTdq_dict["Phi_dqh_mag"] = self.Phi_dqh_mag.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LUTdq_dict["__class__"] = "LUTdq"
        return LUTdq_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.Phi_dqh_mean is None:
            Phi_dqh_mean_val = None
        else:
            Phi_dqh_mean_val = self.Phi_dqh_mean.copy()
        if self.Phi_dqh_mag is None:
            Phi_dqh_mag_val = None
        else:
            Phi_dqh_mag_val = self.Phi_dqh_mag.copy()
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
            Phi_dqh_mean=Phi_dqh_mean_val,
            Phi_dqh_mag=Phi_dqh_mag_val,
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

        self.Phi_dqh_mean = None
        if self.Phi_dqh_mag is not None:
            self.Phi_dqh_mag._set_None()
        # Set to None the properties inherited from LUT
        super(LUTdq, self)._set_None()

    def _get_Phi_dqh_mean(self):
        """getter of Phi_dqh_mean"""
        return self._Phi_dqh_mean

    def _set_Phi_dqh_mean(self, value):
        """setter of Phi_dqh_mean"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("Phi_dqh_mean", value, "ndarray")
        self._Phi_dqh_mean = value

    Phi_dqh_mean = property(
        fget=_get_Phi_dqh_mean,
        fset=_set_Phi_dqh_mean,
        doc="""RMS stator winding flux table in dqh frame (including magnets and currents given by I_dqh)

        :Type: ndarray
        """,
    )

    def _get_Phi_dqh_mag(self):
        """getter of Phi_dqh_mag"""
        return self._Phi_dqh_mag

    def _set_Phi_dqh_mag(self, value):
        """setter of Phi_dqh_mag"""
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
                "pyleecan.Classes", value.get("__class__"), "Phi_dqh_mag"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            DataND = import_class("pyleecan.Classes", "DataND", "Phi_dqh_mag")
            value = DataND()
        check_var("Phi_dqh_mag", value, "DataND")
        self._Phi_dqh_mag = value

        if self._Phi_dqh_mag is not None:
            self._Phi_dqh_mag.parent = self

    Phi_dqh_mag = property(
        fget=_get_Phi_dqh_mag,
        fset=_set_Phi_dqh_mag,
        doc="""RMS stator winding flux linkage spectrum in dqh frame including harmonics (only magnets)

        :Type: DataND
        """,
    )
