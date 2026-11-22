# Experimental pydantic model generated from Generator/ClassesRef/Loss/LossFEA.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...classes_common.errors import FieldMissingError, InputError
from ...classes_common.logger_context import get_logger
from ...classes_common.parents import container_or_parent
from ..output.out_loss_model import OutLossModel
from ..scidatatool.data_1d import Data1D
from ..scidatatool.data_freq import DataFreq
from ..scidatatool.data_time import DataTime
from .loss import Loss
from .loss_model_bertotti import LossModelBertotti
from .loss_model_joule import LossModelJoule
from .loss_model_magnet import LossModelMagnet
from .loss_model_proximity import LossModelProximity
from .loss_model_steinmetz import LossModelSteinmetz
from .loss_model_windage_pyrhonen import LossModelWindagePyrhonen

if TYPE_CHECKING:
    from ..output.output import Output
    from ..scidatatool.data import Data


class LossFEA(Loss):
    """Simplified loss module, with predefined loss models for a quick setup

    Attributes
    ----------
    k_ed_enforced : float or None
        User-defined eddy-current loss coefficient to enforce in Bertotti and Steinmetz iron loss model
        Unit: W/(m3*T2*Hz2); Default: None
    k_hy_enforced : float or None
        User-defined hysteresis loss coefficient to enforce in Bertotti and Steinmetz iron loss model
        Unit: W/(m3*T2*Hz); Default: None
    k_p_enforced : float or None
        User-defined proximity loss coefficient to enforce in proximity loss model
        Unit: W/(m3*T2*Hz2); Default: None
    type_skin_effect : int
        Skin effect for resistance calculation (0 to ignore skin effect, 1 to consider it)
        Default: 1
    type_loss_model_core : str
        Loss model for iron cores : "Bertotti" or "Steinmetz"
        Default: "Steinmetz"
    is_stacking_factor : bool
        True to consider lamination stacking factor when calculating core losses
        Default: True
    k_ex_enforced : float or None
        User-defined hysteresis loss coefficient to enforce in Bertotti iron loss model
        Unit: W/(m3*T2*Hz2); Default: None
    alpha_B_enforced : float or None
        User-defined hysteresis loss exponent for flux density to enforce for in Bertotti and Steinmetz model
        Default: None
    is_calc_windage_loss : bool
        True to calculate windage losses in the airgap
        Default: False
    alpha_f_enforced : float or None
        User-defined hysteresis loss exponent for frequency to enforce for in Steinmetz model
        Default: None
    is_dynamic : bool
        False to calculate average losses in frequency domain, True to calculate dynamic losses over time (not validated yet)
        Default: False
    """

    k_ed_enforced: float | None = Field(
        default=None, json_schema_extra={"unit": "W/(m3*T2*Hz2)"}
    )
    """User-defined eddy-current loss coefficient to enforce in Bertotti and Steinmetz iron loss model"""
    k_hy_enforced: float | None = Field(
        default=None, json_schema_extra={"unit": "W/(m3*T2*Hz)"}
    )
    """User-defined hysteresis loss coefficient to enforce in Bertotti and Steinmetz iron loss model"""
    k_p_enforced: float | None = Field(
        default=None, json_schema_extra={"unit": "W/(m3*T2*Hz2)"}
    )
    """User-defined proximity loss coefficient to enforce in proximity loss model"""
    type_skin_effect: int = 1
    """Skin effect for resistance calculation (0 to ignore skin effect, 1 to consider it)"""
    type_loss_model_core: str = "Steinmetz"
    """Loss model for iron cores : "Bertotti" or "Steinmetz\""""
    is_stacking_factor: bool = True
    """True to consider lamination stacking factor when calculating core losses"""
    k_ex_enforced: float | None = Field(
        default=None, json_schema_extra={"unit": "W/(m3*T2*Hz2)"}
    )
    """User-defined hysteresis loss coefficient to enforce in Bertotti iron loss model"""
    alpha_B_enforced: float | None = None
    """User-defined hysteresis loss exponent for flux density to enforce for in Bertotti and Steinmetz model"""
    is_calc_windage_loss: bool = False
    """True to calculate windage losses in the airgap"""
    alpha_f_enforced: float | None = None
    """User-defined hysteresis loss exponent for frequency to enforce for in Steinmetz model"""
    is_dynamic: bool = False
    """False to calculate average losses in frequency domain, True to calculate dynamic losses over time (not validated yet)"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Loss.LossFEA.comp_axes
    def comp_axes(self, output: Output) -> tuple[dict[str, Data], bool]:
        """Compute the axes required in Loss module

        Parameters
        ----------
        self : LossFEA
            a LossFEA object
        output : Output
            an Output object (to update)

        Returns
        -------
        axes_dict: {Data}
            Dict containing Time (including (anti-)periodicties) and Indices axes used in any Loss module
        is_mirror : bool
            True to mirror magnetic mesh quantities calculate in stator and rotor frames to get the same Time axis
        """

        # Load axes dict from Outmag
        axes_dict_mag = output.mag.axes_dict
        if axes_dict_mag is None:
            raise FieldMissingError(
                "OutMag.axes_dict is None: the magnetic axes are not computed"
            )

        # Load Time axes depending on stator and rotor periodicities
        # Check if Magnetic mesh data is calculated in rotor and stator frames with different time periodicities
        if "time_S" in axes_dict_mag and "time_R" in axes_dict_mag:
            Time_S = axes_dict_mag["time_S"].copy()
            Time_R = axes_dict_mag["time_R"].copy()

            if "antiperiod" in Time_S.symmetries:
                # There is no anti-periodicity for losses calculation since there is a constant value
                Time_S.symmetries = {"period": Time_S.symmetries["antiperiod"]}

            assert "antiperiod" not in Time_R.symmetries

            # Compare time period length between stator frame and rotor frame
            time_val_S = Time_S.get_values(is_oneperiod=True)
            time_val_R = Time_R.get_values(is_oneperiod=True)

            if time_val_S[-1] == time_val_R[-1]:
                # Same period value for both stator and rotor frames, no need to mirror any loss values
                is_mirror = False
                Time = Time_S  # Time_S and Time_R are the same
            elif time_val_S[-1] > time_val_R[-1]:
                # Stator period is longer, rotor loss values has to mirrored
                if "period" in Time_S.symmetries:
                    per_t = int(Time_S.symmetries["period"])
                else:
                    per_t = 1
                Time = Time_S.get_axis_periodic(Nper=per_t, is_aper=False)
                is_mirror = True
            else:
                # Rotor period is longer, stator loss values has to mirrored
                if "period" in Time_R.symmetries:
                    per_t = int(Time_R.symmetries["period"])
                else:
                    per_t = 1
                Time = Time_R.get_axis_periodic(Nper=per_t, is_aper=False)
                is_mirror = True

        else:
            # Same time periodicity for both stator and rotor frames
            Time = axes_dict_mag["time"].copy()
            is_mirror = False

        # Store time axes in axes_dict for time calculation
        axes_dict = {"time": Time}

        # Store frequency axis in axes_dict for frequency calculation (only average loss value is calculated by frequency model)
        axes_dict["freqs"] = Data1D(
            name="freqs",
            unit="Hz",
            values=[0.0],
            normalizations=Time.normalizations.copy(),
        )

        # Add element indices axis for mesh calculation and plotting
        axes_dict["indice_element"] = axes_dict_mag["indice_element"].copy()

        return axes_dict, is_mirror

    # Inlined from Methods.Loss.LossFEA.run
    def run(self, output: Output | None = None) -> None:
        """Run the LossFEA module

        Parameters
        ----------
        output : Output, optional
            Output of the simulation (default: the parent of the simulation)

        Paramaters
        ----------
        self : LossFEA
            A LossFEA object
        """
        output = container_or_parent(self, output, "output", depth=2)
        if output is None and container_or_parent(self, None, "simu") is None:
            raise InputError("The LossFEA object must be in a Simulation object to run")
        if output is None:
            raise InputError("The LossFEA object must be in an Output object to run")

        get_logger(self).info("Starting Loss module")
        get_logger(self).info("Computing losses with LossFEA model")

        # get output

        # Get fundamental frequency
        felec = output.elec.OP.get_felec()

        if output.mag.meshsolution is None:
            raise InputError(
                "The LossFEA object must use a magnetic meshsolution calculated by a magnetics FEA model to run"
            )

        if self.type_loss_model_core not in ["Bertotti", "Steinmetz"]:
            raise InputError(
                "The LossFEA object only accepts ['Bertotti','Steinmetz'] as self.type_loss_model_core"
            )

        axes_dict, is_mirror = self.comp_axes(output)

        # Get mesh groups names
        list_group = list(output.mag.meshsolution.group)

        # Define all relevant loss models
        self.model_dict = {}
        if "stator core" in list_group:
            if self.type_loss_model_core == "Bertotti":
                self.model_dict["stator core"] = LossModelBertotti(
                    group="stator core",
                    k_hy=self.k_hy_enforced,
                    k_ed=self.k_ed_enforced,
                    k_ex=self.k_ex_enforced,
                    alpha_B=self.alpha_B_enforced,
                    is_stacking_factor=self.is_stacking_factor,
                )
            elif self.type_loss_model_core == "Steinmetz":
                self.model_dict["stator core"] = LossModelSteinmetz(
                    group="stator core",
                    k_hy=self.k_hy_enforced,
                    k_ed=self.k_ed_enforced,
                    alpha_f=self.alpha_f_enforced,
                    alpha_B=self.alpha_B_enforced,
                    is_stacking_factor=self.is_stacking_factor,
                )

        if "stator winding" in list_group:
            self.model_dict["stator joule"] = LossModelJoule(
                group="stator winding", type_skin_effect=self.type_skin_effect
            )
            self.model_dict["stator proximity"] = LossModelProximity(
                group="stator winding", k_p=self.k_p_enforced
            )

        if "rotor core" in list_group:
            if self.type_loss_model_core == "Bertotti":
                self.model_dict["rotor core"] = LossModelBertotti(
                    group="rotor core",
                    k_hy=self.k_hy_enforced,
                    k_ed=self.k_ed_enforced,
                    k_ex=self.k_ex_enforced,
                    alpha_B=self.alpha_B_enforced,
                    is_stacking_factor=self.is_stacking_factor,
                )
            elif self.type_loss_model_core == "Steinmetz":
                self.model_dict["rotor core"] = LossModelSteinmetz(
                    group="rotor core",
                    k_hy=self.k_hy_enforced,
                    k_ed=self.k_ed_enforced,
                    alpha_f=self.alpha_f_enforced,
                    alpha_B=self.alpha_B_enforced,
                    is_stacking_factor=self.is_stacking_factor,
                )

        if "rotor magnets" in list_group:
            self.model_dict["rotor magnets"] = LossModelMagnet(group="rotor magnets")

        if self.is_calc_windage_loss and "airgap" in list_group:
            self.model_dict["airgap windage"] = LossModelWindagePyrhonen(group="airgap")

        loss_dict = {}
        group_all, name_all = "", ""
        for group_name, model in self.model_dict.items():
            if self.is_dynamic:
                loss_density, loss_val_dict = model.comp_loss_time(
                    axes_dict, is_mirror=is_mirror, loss=self, output=output
                )
            else:
                loss_density, loss_val_dict, freqs = model.comp_loss_freq(
                    loss=self, output=output
                )

            loss_mean = 0
            list_loss_val = []
            for key, val in loss_val_dict.items():
                if "losses" in key:
                    # Ignore dict entries without losses in it since they are contributions to the loss type (e.g. hysteresis/eddy-current/excess for Bertotti iron losses)
                    if self.is_dynamic:
                        # Average over time step
                        loss_mean = val.mean()
                    else:
                        # Sum over frequency
                        loss_mean = val.sum()
                list_loss_val.append(val[:, None])

            Ax_losses = Data1D(
                name="type",
                unit=" ",
                values=list(loss_val_dict.keys()),
                is_components=True,
                is_overlay=True,
                filter={"type": []},
            )

            if self.is_dynamic:
                loss_data = DataTime(
                    name=group_name,
                    symbol="L",
                    unit="W",
                    values=np.hstack(list_loss_val),
                    axes=[axes_dict["time"].copy(), Ax_losses],
                )

            else:
                Freqs = Data1D(
                    name="freqs",
                    unit="Hz",
                    values=freqs,
                    normalizations=axes_dict["time"].normalizations.copy(),
                )
                loss_data = DataFreq(
                    name=group_name,
                    symbol="L",
                    unit="W",
                    values=np.hstack(list_loss_val),
                    axes=[Freqs, Ax_losses],
                )
            # Store results of each model in a different object
            loss_dict[group_name] = OutLossModel(
                name=group_name,
                loss_density=loss_density,
                scalar_value=loss_mean,
                group=model.group,
                loss_model=type(model).__name__,
                loss_data=loss_data,
                coeff_dict=model.coeff_dict.copy(),
            )

            if not self.is_dynamic:
                # Check consistency of scalar_value and coeff_dict
                diff = loss_mean - loss_dict[group_name].get_loss_scalar(felec)
                np.testing.assert_almost_equal(diff, 0)

            # Concatenate model group and name for the overall OutLossModel
            group_all += model.group + " + "
            name_all += group_name + " + "

        # Storing axes_dict in OutLoss (requested for OutLoss.get_meshsolution)
        output.loss.axes_dict = axes_dict

        # Storing loss_dict in OutLoss (requested for OutLoss.get_meshsolution)
        output.loss.loss_dict = loss_dict
        loss_dict = output.loss.loss_dict  # The stored dict

        # Calculate meshsolution to get overall loss density
        output.loss.get_meshsolution(output=output)
        loss_density_all = output.loss.meshsolution["L"].field.values

        # Add overall OutLossModel by adding all losses sources
        coeff_dict_all = {}
        for group_name, model in loss_dict.items():
            if model.coeff_dict is None:
                raise FieldMissingError(
                    f"OutLossModel.coeff_dict is None: the loss model {group_name!r} has no coefficients"
                )
            for key, value in model.coeff_dict.items():
                if key in coeff_dict_all:
                    coeff_dict_all[key] += value
                else:
                    coeff_dict_all[key] = value

        output.loss.loss_dict["overall"] = OutLossModel(
            name=name_all[:-3],  # Remove last " + "
            loss_density=loss_density_all,
            coeff_dict=coeff_dict_all,
            group=group_all[:-3],  # Remove last " + "
        )

        # Store input power
        output.loss.P_in = output.mag.Pem_av + loss_dict["stator joule"].scalar_value

        # Store output power
        loss_overall = loss_dict["overall"].get_loss_scalar(felec, output=output)
        output.loss.P_out = output.loss.P_in - loss_overall

        # Store efficiency
        output.loss.efficiency = output.loss.P_out / output.loss.P_in

        # Store mechanical torque
        output.loss.Tmech_av = output.loss.P_out / (2 * np.pi * output.elec.OP.N0 / 60)

        if not self.is_get_meshsolution:
            # Remove meshsolution in OutLoss if loss meshsolution not requested
            output.loss.meshsolution = None

        if self.is_clean_magmesh and not output.simu.mag.is_get_meshsolution:
            # Remove magnetic meshsolution in OutMag if clean is requested
            output.mag.meshsolution = None
