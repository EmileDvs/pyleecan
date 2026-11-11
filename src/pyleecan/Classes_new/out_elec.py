# Experimental dataclass generated from Generator/ClassesRef/Output/OutElec.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..Functions_new.Electrical.dqh_transformation import dqh2n_DataTime, n2dqh_DataTime
from ..Functions_new.Electrical.dqh_transformation_freq import (
    dqh2n_DataFreq,
    n2dqh_DataFreq,
)
from ._pyleecan_class import PyleecanClass
from .data import Data
from .data_1d import Data1D
from .data_freq import DataFreq
from .data_nd import DataND
from .data_time import DataTime
from .eec import EEC
from .import_gen_pwm import ImportGenPWM
from .op import OP
from .out_internal import OutInternal


@dataclass(eq=False)
class OutElec(PyleecanClass):
    """Gather the electric module outputs

    Attributes
    ----------
    axes_dict : {Data} or None
        Dict containing axes data used for Electrical
        Default: None
    Is : DataND or None
        Stator currents DataTime object
        Unit: A; Default: None
    Ir : DataND or None
        Rotor currents as a function of time (each column correspond to one phase)
        Unit: A; Default: None
    logger_name : str
        Name of the logger to use
        Default: "pyleecan.Electrical"
    Pj_losses : float or None
        Electrical Joule losses
        Unit: W; Default: None
    Us : DataND or None
        Stator voltage as a function of time (each column correspond to one phase)
        Unit: V; Default: None
    internal : OutInternal or None
        OutInternal object containg outputs related to a specific model
        Default: None
    OP : OP or None
        Operating Point
        Default: None
    Pem_av : float or None
        Average Electromagnetic power
        Unit: W; Default: None
    Tem_av : float or None
        Average Electromagnetic torque
        Unit: N.m; Default: None
    phase_dir : int or None
        Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)
        Default: None; Minimum: -1; Maximum: 1
    current_dir : int or None
        Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)
        Default: None; Minimum: -1; Maximum: 1
    PWM : ImportGenPWM or None
        Object to generate PWM signal
        Default: None
    eec : EEC or None
        Electric Equivalent Circuit used for OP resolution
        Default: None
    P_out : float or None
        Output power
        Unit: W; Default: None
    Jrms : float or None
        RMS current density in slots
        Unit: A/m2; Default: None; Minimum: 0
    P_in : float or None
        Input power
        Unit: W; Default: None
    Arms : float or None
        RMS linear current density along airgap
        Unit: A/m; Default: None
    Erms : float or None
        RMS back-emf
        Unit: V; Default: None
    """

    axes_dict: dict[str, Data] | None = None
    """Dict containing axes data used for Electrical"""
    Is: DataND | None = field(default=None, metadata={"default_class": "DataND"})
    """Stator currents DataTime object"""
    Ir: DataND | None = field(default=None, metadata={"default_class": "DataND"})
    """Rotor currents as a function of time (each column correspond to one phase)"""
    logger_name: str = "pyleecan.Electrical"
    """Name of the logger to use"""
    Pj_losses: float | None = None
    """Electrical Joule losses"""
    Us: DataND | None = field(default=None, metadata={"default_class": "DataND"})
    """Stator voltage as a function of time (each column correspond to one phase)"""
    internal: OutInternal | None = field(
        default=None, metadata={"default_class": "OutInternal"}
    )
    """OutInternal object containg outputs related to a specific model"""
    OP: OP | None = field(default=None, metadata={"default_class": "OP"})
    """Operating Point"""
    Pem_av: float | None = None
    """Average Electromagnetic power"""
    Tem_av: float | None = None
    """Average Electromagnetic torque"""
    phase_dir: int | None = None
    """Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)"""
    current_dir: int | None = None
    """Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)"""
    PWM: ImportGenPWM | None = field(
        default=None, metadata={"default_class": "ImportGenPWM"}
    )
    """Object to generate PWM signal"""
    eec: EEC | None = field(default=None, metadata={"default_class": "EEC"})
    """Electric Equivalent Circuit used for OP resolution"""
    P_out: float | None = None
    """Output power"""
    Jrms: float | None = None
    """RMS current density in slots"""
    P_in: float | None = None
    """Input power"""
    Arms: float | None = None
    """RMS linear current density along airgap"""
    Erms: float | None = None
    """RMS back-emf"""

    # Inlined from Methods.Output.OutElec.get_electrical
    def get_electrical(
        self,
        data_dict,
        Time=None,
        is_dqh=False,
        is_fund_only=False,
        is_harm_only=False,
        is_freq=None,
    ):
        """Generic getter to return voltage/current as DataND object

        Parameters
        ----------
        self : OutElec
            an OutElec object
        data_dict: str
            Requested quantity ('U_s': stator voltage, 'I_s': stator current)
        Time : Data
            Time axis
        is_dqh : bool
            True to rotate in DQH frame
        is_fund_only : bool
            True to return only fundamental component
        is_harm_only : bool
            True to return only components at higher frequencies than fundamental component
        is_freq: bool
            True to calculate dqh transformation in frequency domain

        Returns
        -------
        obj: DataND
            Requested quantity
        """

        if is_fund_only and is_harm_only:
            raise Exception("is_fund_only and is_harm_only cannot be both True")

        # Get object from OutElec
        quantity = data_dict["symbol"].replace("_", "")
        obj = getattr(self, quantity)

        # Get requested quantity in data_dict
        if obj is None:
            if Time is None:
                Time = self.axes_dict["time"]

            lamination = self.parent.simu.machine.get_lam_by_label(
                data_dict["lam_label"]
            )

            # Recalculate quantity
            qs = lamination.winding.qs
            phase_label = "phase_" + data_dict["lam_label"]
            Phase = self.axes_dict[phase_label].copy()
            if is_freq:
                N = 1
                Freqs = Data1D(
                    name="freqs",
                    symbol="",
                    unit="Hz",
                    normalizations=Time.normalizations.copy(),
                    is_components=Time.is_components,
                    values=np.array([0]),
                )
                axes_list = [Freqs, Phase]
                DataClass = DataFreq
            else:
                N = Time.get_length(is_smallestperiod=True)
                Time_bis = Time.copy()
                is_aper = False
                if "antiperiod" in Time_bis.symmetries:
                    is_aper = True
                    Time_bis.symmetries["period"] = Time_bis.symmetries.pop(
                        "antiperiod"
                    )
                axes_list = [Time_bis, Phase]
                DataClass = DataTime

            # Generate quantity according to Ad/Aq, Ah=0
            if (
                data_dict["Ad"] is not None
                and data_dict["Aq"] is not None
                and (data_dict["Ad"] != 0 or data_dict["Aq"] != 0)
            ):
                # Generate constant dqh values along time
                A_val = np.zeros((N, 3))
                A_val[:, 0] = data_dict["Ad"]
                A_val[:, 1] = data_dict["Aq"]
            else:
                # Enforce zero values in quantity
                A_val = np.zeros((N, qs))

            A_dqh = DataClass(
                name=data_dict["name"],
                unit=data_dict["unit"],
                symbol=data_dict["symbol"],
                axes=axes_list,
                values=A_val,
            )

            # Check requested referential
            if is_dqh:
                obj = A_dqh
            elif is_freq:
                obj = dqh2n_DataFreq(
                    A_dqh,
                    n=qs,
                    current_dir=self.current_dir,
                    felec=self.OP.felec,
                    is_n_rms=False,
                    phase_dir=self.phase_dir,
                )
            else:
                obj = dqh2n_DataTime(
                    A_dqh, n=qs, is_n_rms=False, phase_dir=self.phase_dir
                )
                if is_aper:
                    obj.axes[0].symmetries["antiperiod"] = obj.axes[0].symmetries.pop(
                        "period"
                    )

        else:
            if Time is not None:
                # Interpolate values on Time vector
                obj = obj.get_data_along(
                    "time=axis_data", "phase", axis_data={"time": Time.get_values()}
                )

            if is_dqh:
                # Convert to DQH frame
                if is_freq:
                    obj = n2dqh_DataFreq(
                        obj,
                        is_dqh_rms=True,
                        phase_dir=self.phase_dir,
                        current_dir=self.current_dir,
                        felec=self.OP.get_felec(),
                    )
                else:
                    obj = n2dqh_DataTime(obj, is_dqh_rms=True, phase_dir=self.phase_dir)

        if is_fund_only or is_harm_only:
            if Time is None and not is_dqh:
                # Copy object to leave original object unchanged
                obj = obj.copy()

            # Fundamental is at felec in ABC frame, 0Hz in dqh frame
            felec = (1 - int(is_dqh)) * self.OP.get_felec()
            # Get data object with quantity harmonics higher than fundamental component
            obj = obj.get_data_along("freqs", "phase")
            # Get index of fundamental frequency
            Freqs = obj.axes[0]
            freqs = Freqs.get_values()
            ifund = np.argmin(np.abs(freqs - felec))

            if is_fund_only:
                # Keep only fundamental frequency
                Freqs_fund = Data1D(
                    name=Freqs.name,
                    symbol=Freqs.symbol,
                    unit=Freqs.unit,
                    normalizations=Freqs.normalizations,
                    is_components=Freqs.is_components,
                    values=np.array([freqs[ifund]]),
                )
                obj.axes[0] = Freqs_fund
                obj.values = obj.values[ifund, ...]

            elif is_harm_only:
                # Find all indices
                iharm = [ii for ii in range(freqs.size) if ii != ifund]
                # Remove fundamental frequency component
                Freqs_harm = Data1D(
                    name=Freqs.name,
                    symbol=Freqs.symbol,
                    unit=Freqs.unit,
                    normalizations=Freqs.normalizations,
                    is_components=Freqs.is_components,
                    values=freqs[iharm],
                )
                obj.axes[0] = Freqs_harm
                obj.values = obj.values[iharm, ...]

        return obj

    # Inlined from Methods.Output.OutElec.get_Is
    def get_Is(
        self,
        Time=None,
        is_dqh=False,
        is_fund_only=False,
        is_harm_only=False,
        is_freq=None,
    ):
        """Return the stator current DataND object

        Parameters
        ----------
        self : OutElec
            an OutElec object
        Time : Data
            Time axis
        is_dqh : bool
            True to rotate in DQH frame
        is_fund_only : bool
            True to return only fundamental component
        is_harm_only : bool
            True to return only components at higher frequencies than fundamental component
        is_freq: bool
            True to calculate dqh transformation in frequency domain

        Returns
        -------
        Is: DataND
            stator current
        """

        label = self.parent.simu.machine.stator.get_label()
        Idq_dict = self.OP.get_Id_Iq()

        data_dict = {
            "name": "Stator current",
            "unit": "A",
            "symbol": "I_s",
            "lam_label": label,
            "Ad": Idq_dict["Id"],
            "Aq": Idq_dict["Iq"],
        }

        Is = self.get_electrical(
            data_dict,
            Time=Time,
            is_dqh=is_dqh,
            is_fund_only=is_fund_only,
            is_harm_only=is_harm_only,
            is_freq=is_freq,
        )

        return Is

    # Inlined from Methods.Output.OutElec.get_Jrms
    def get_Jrms(self):
        """Return the stator current density rms value

        Parameters
        ----------
        self : OutElec
            an OutElec object

        Returns
        -------
        Jrms: float
            stator current density rms value [A/m^2]
        """

        if self.Jrms is None:
            output = self.parent
            machine = output.simu.machine

            Swire = machine.stator.winding.conductor.comp_surface_active()
            Npcp = machine.stator.winding.Npcp

            Idq_dict = self.OP.get_Id_Iq()

            self.Jrms = np.sqrt(Idq_dict["Id"] ** 2 + Idq_dict["Iq"] ** 2) / (
                Swire * Npcp
            )

        return self.Jrms

    # Inlined from Methods.Output.OutElec.get_Nr
    def get_Nr(self, Time=None):
        """Create speed in function of time vector Nr

        Parameters
        ----------
        self : OutElec
            An OutElec object
        Time : Data
            a time axis (SciDataTool Data object)

        Returns
        -------
        Nr: ndarray
            speed in function of time
        """

        if Time is None:
            if self.axes_dict is not None and "time" in self.axes_dict:
                Time = self.axes_dict["time"]
            else:
                raise Exception('You must define "time" property before calling get_Nr')

        if self.OP.get_N0() is None:
            raise Exception('You must define "N0" before calling get_Nr')

        # Same speed for every timestep
        Nr = self.OP.get_N0() * np.ones(Time.get_length(is_smallestperiod=True))

        return Nr

    # Inlined from Methods.Output.OutElec.get_Us
    def get_Us(
        self,
        Time=None,
        is_dqh=False,
        is_fund_only=False,
        is_harm_only=False,
        is_freq=None,
    ):
        """Return the fundamental stator voltage as DataND object

        Parameters
        ----------
        self : OutElec
            an OutElec object
        Time : Data
            Time axis
        is_dqh : bool
            True to rotate in DQH frame
        is_fund_only : bool
            True to return only fundamental component
        is_harm_only : bool
            True to return only components at higher frequencies than fundamental component
        is_freq: bool
            True to calculate dqh transformation in frequency domain

        Returns
        -------
        Us: DataND
            stator voltage
        """

        label = self.parent.simu.machine.stator.get_label()
        Udq_dict = self.OP.get_Ud_Uq()

        data_dict = {
            "name": "Stator voltage",
            "unit": "V",
            "symbol": "U_s",
            "lam_label": label,
            "Ad": Udq_dict["Ud"],
            "Aq": Udq_dict["Uq"],
        }

        Us = self.get_electrical(
            data_dict,
            Time=Time,
            is_dqh=is_dqh,
            is_fund_only=is_fund_only,
            is_harm_only=is_harm_only,
            is_freq=is_freq,
        )

        return Us

    # Inlined from Methods.Output.OutElec.store
    def store(self, out_dict):
        """Store the standard outputs of Electrical that are temporarily in out_dict as arrays into OutElec as Data object

        Parameters
        ----------
        self : OutElec
            the OutElec object to update
        out_dict : dict
            Dict containing all electrical quantities that have been calculated in EEC

        """

        output = self.parent
        machine = output.simu.machine

        # Store Id, Iq, Ud, Uq in OP
        self.OP.set_Id_Iq(Id=out_dict["Id"], Iq=out_dict["Iq"])
        self.OP.set_Ud_Uq(Ud=out_dict["Ud"], Uq=out_dict["Uq"])

        self.Pj_losses = out_dict["Pj_losses"]
        self.Tem_av = out_dict["Tem_av"]
        self.Pem_av = out_dict["Pem_av"]
        self.get_Jrms()

        if "Ir" in out_dict and self.OP.get_slip() != 0:
            # Calculate rotor currents for each bar
            p = machine.get_pole_pair_number()
            Zr = machine.rotor.get_Zs()
            rotor_lab = machine.rotor.get_label()
            Phase = self.axes_dict["phase_" + rotor_lab]

            Time = self.axes_dict["time"]

            angle_bars = Phase.get_values(is_smallestperiod=True)

            phase_dir = output.elec.phase_dir
            d_angle = machine.stator.comp_angle_d_axis()

            # Get rotor current fundamental given by EEC
            if phase_dir == -1:
                Ir_fund = np.conj(out_dict["Ir"])
            else:
                Ir_fund = out_dict["Ir"]
            # Get phase angle of stator mmf fundamental
            phimax = 2 * np.pi - p * d_angle
            # Mechanical phase of first bar: q-axis phase + half of rotor slot pitch
            PhiMech = phimax + np.pi / 2 + p * np.pi / Zr

            Ir_val = np.zeros((2, angle_bars.size), dtype=complex)
            Ir_val[1, :] = Ir_fund * np.exp(
                -phase_dir * 1j * (p * angle_bars + PhiMech)
            )

            felec_rot = self.OP.get_felec() * self.OP.get_slip()

            norm_freq = {}
            if Time.normalizations is not None and len(Time.normalizations) > 0:
                for key, val in Time.normalizations.items():
                    norm_freq[key] = val.copy()

            Freqs = Data1D(
                name="freqs",
                symbol="",
                unit="Hz",
                values=np.array([0, felec_rot]),
                normalizations=norm_freq,
            )

            self.Ir = DataFreq(
                name="Rotor current",
                unit="A",
                symbol="Ir",
                axes=[Freqs, Phase],
                values=Ir_val,
            )

            # Ir = self.Ir.get_data_along(
            #     "time=axis_data",
            #     "phase[smallestperiod]",
            #     axis_data={"time": Time.get_values()},
            # )

            # Ir.plot_3D_Data("time", "phase", is_shading_flat=True)

        if "Is_PWM" in out_dict:
            # Merge current PWM harmonics with fundamental current
            # Get PWM current from out_dict
            Is_PWM = out_dict.pop("Is_PWM")

            # Merge Spectrums
            # Get fundamental current spectrum
            Is = self.get_Is(is_freq=True)
            Is_fund = Is.get_along("freqs=" + str(self.OP.felec), "phase")[Is.symbol]
            # Get PWM frequency vector
            freqs = Is_PWM.axes[0].get_values()
            Ifund = np.where(np.abs(freqs - self.OP.felec) < 1e-4)[0]
            if Ifund.size == 0:
                # Add felec at the first place
                freqs = np.insert(freqs, 0, self.OP.felec, axis=0)
                # Add fundamental values
                Is_val = np.insert(Is_PWM.values, 0, Is_fund, axis=0)
                # Store values in Is
                Isort = np.argsort(freqs)
                Is.axes[0].values = freqs[Isort]
                Is.values = Is_val[Isort, :]
            else:
                # felec already in frequency axis, simply replace by fundamental value
                Is.axes[0].values = freqs
                Is_PWM.values[Ifund, :] = Is_fund
                Is.values = Is_PWM.values

            # Store current in OutElec
            self.Is = Is
