# Experimental dataclass generated from Generator/ClassesRef/Output/LUTdq.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np
import scipy.interpolate as scp_int

from ..Functions_new.Electrical.dqh_transformation import n2dqh_DataTime
from .data_nd import DataND
from .eec_pmsm import EEC_PMSM
from .electrical import Electrical
from .lut import LUT


@dataclass(eq=False)
class LUTdq(LUT):
    """Look Up Table class for dq OP matrix

    Attributes
    ----------
    Phi_dqh_mean : ndarray or None
        RMS stator winding flux table in dqh frame (including magnets and currents given by I_dqh)
        Unit: Wbrms; Default: None
    Phi_dqh_mag : DataND or None
        RMS stator winding flux linkage spectrum in dqh frame including harmonics (only magnets)
        Unit: Wbrms; Default: None
    """

    Phi_dqh_mean: np.ndarray | None = None
    """RMS stator winding flux table in dqh frame (including magnets and currents given by I_dqh)"""
    Phi_dqh_mag: DataND | None = field(
        default=None, metadata={"default_class": "DataND"}
    )
    """RMS stator winding flux linkage spectrum in dqh frame including harmonics (only magnets)"""

    # Inlined from Methods.Output.LUTdq.get_index_open_circuit
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

    # Inlined from Methods.Output.LUTdq.get_L_dqh
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

    # Inlined from Methods.Output.LUTdq.get_Lm_dqh
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

    # Inlined from Methods.Output.LUTdq.get_Phi_dqh_mag
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

    # Inlined from Methods.Output.LUTdq.get_Phi_dqh_mag_mean
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

    # Inlined from Methods.Output.LUTdq.get_Phi_dqh_mean
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

    # Inlined from Methods.Output.LUTdq.interp_Phi_dqh
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

    # Inlined from Methods.Output.LUTdq.interp_Ploss_dqh
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

    # Inlined from Methods.Output.LUTdq.interp_Tem_rip_dqh
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
