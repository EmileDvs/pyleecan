import numpy as np
import pandas as pd

from pyleecan.Functions.load import load

from losses.comp_loss import comp_loss


def postprocess_all(path_dict, is_dqh_rms=False):

    out_dict = {}

    elec_val_dict = {}
    current_dict = {}
    voltage_dict = {}

    mag_val_dict = {}
    tem_dict = {}
    emf_dict = {}
    mag_ms_dict = {}

    loss_dt_dict = {}
    loss_ms_dict = {}
    loss_val_dict = {}

    for out_name, path in path_dict.items():
        out = load(path)

        out_dict[out_name] = out

        current_dict[out_name] = out.elec.get_Is()

        voltage_dict[out_name] = out.elec.get_Us()

        (
            elec_val_dict[out_name],
            mag_val_dict[out_name],
            loss_val_dict[out_name],
            loss_dt_dict[out_name],
            loss_ms_dict[out_name],
        ) = postprocess(out, is_dqh_rms)

        tem_dict[out_name] = out.mag.Tem

        emf_dict[out_name] = out.mag.emf

        mag_ms_dict[out_name] = out.mag.meshsolution

    simu_list = list(path_dict.keys())

    quantity_list = list(elec_val_dict[simu_list[0]].keys())
    quantity_list.extend(list(mag_val_dict[simu_list[0]].keys()))
    quantity_list.extend(list(loss_val_dict[simu_list[0]].keys()))

    values_list = []
    for name in simu_list:
        values_simu = list(elec_val_dict[name].values())
        values_simu.extend(list(mag_val_dict[name].values()))
        values_simu.extend(list(loss_val_dict[name].values()))
        values_list.append(np.array(values_simu, dtype=object))

    motor_db = pd.DataFrame(
        columns=quantity_list, index=simu_list, data=np.array(values_list, dtype=object)
    )
    return (
        motor_db,
        out_dict,
        current_dict,
        voltage_dict,
        tem_dict,
        emf_dict,
        mag_ms_dict,
        loss_dt_dict,
        loss_ms_dict,
    )


def postprocess(out, is_dqh_rms=False):

    Tperiod = 1 / out.elec.OP.get_felec()

    result = out.elec.get_Is().get_along("time", "phase[]")
    t = result["time"]
    Is_val = result["I_s"]

    Us_val = out.elec.get_Us().get_along(
        "time=axis_data", "phase[]", axis_data={"time": t}
    )["U_s"]

    # Calculate voltage RMS value:
    Vrms = np.mean(np.std(Us_val, axis=0))

    # Calculate current RMS value:
    Irms = np.mean(np.std(Is_val, axis=0))

    # Calculate emf RMS:
    Us_fea_val = out.mag.emf.get_along("time", "phase[]")[out.mag.emf.symbol]
    Vrms_fea = np.mean(np.std(Us_fea_val, axis=0)) + out.simu.elec.eec.R1 * Irms

    if is_dqh_rms:
        dq_str = "rms"
        dq_factor = 1.0
    else:
        dq_str = "peak"
        dq_factor = np.sqrt(2)

    ke_1 = 60 / (2 * np.pi * np.sqrt(3) * out.simu.elec.eec.Phid_mag)
    ke_2 = out.simu.elec.eec.Phid_mag
    Erms = 2 * np.pi * out.elec.eec.OP.N0 / 60 * out.simu.elec.eec.Phid_mag

    # Calculate active power : 1/T*integral(u*i*dt, 0, T) summed over phases
    active_power = np.sum(np.trapz(Us_val * Is_val, t, axis=0)) / Tperiod

    # Calculate fft
    Nfreq = int(t.size / 2)
    Vout_fft = np.fft.fft(Us_val[:, 0])[:Nfreq] / Nfreq

    # Voltage Total Harmonic Distortion (THD) : sqrt(sum(V_k^2, 2, K)/sum(V_k^2, 1, K))
    V_THD = 100 * np.sqrt(
        np.sum(np.abs(Vout_fft[2:]) ** 2) / np.sum(np.abs(Vout_fft[1:] ** 2))
    )

    if out.elec.PWM is not None:
        M_I = out.elec.PWM.get_modulation_index()
        fswi = out.elec.PWM.fswi
    else:
        M_I = 0
        fswi = 0

    if np.abs(out.elec.eec.OP.Iq_ref) > 1e-6:
        # Calculate power factor : PF = (Active Power)/(Urms*Irms)
        power_factor = active_power / (3 * Vrms * Irms)
        Iout_fft = np.fft.fft(Is_val[:, 0])[:Nfreq] / Nfreq

        # Current Total Harmonic Distortion (THD)
        I_THD = 100 * np.sqrt(
            np.sum(np.abs(Iout_fft[2:]) ** 2) / np.sum(np.abs(Iout_fft[1:] ** 2))
        )

        # Calculate phase shift between output current and output voltage
        V_out_I_out_phase_shift = (
            (np.angle(Iout_fft[1]) - np.angle(Vout_fft[1])) * 180 / np.pi
        )
        kt = out.mag.Tem_av / out.elec.eec.OP.Iq_ref

    else:
        power_factor = 0
        I_THD = 0
        V_out_I_out_phase_shift = 0
        kt = 0

    if "no_load" in out.simu.name:
        control_type = "No-load"
    elif "sine" in out.simu.name:
        control_type = "Ideal sine current"
    elif "spwm" in out.simu.name:
        control_type = "Sine-Triangle PWM"
    elif "svpwm" in out.simu.name:
        control_type = "Space-Vector PWM"
    elif "6step" in out.simu.name:
        if "pwm" in out.simu.name:
            control_type = "PWM 6-step"
        else:
            control_type = "PAM 6-step"
    elif "celeroton" in out.simu.name:
        control_type = "PAM Celeroton"
    else:
        control_type = " "

    elec_val_dict = {
        "Motor type": out.simu.name[:3],
        "Control type": control_type,
        "Rotor mechanical speed [krpm]": out.elec.eec.OP.N0 * 1e-3,
        "Motor length [mm]": out.simu.machine.stator.L1 * 1e3,
        "Stator winding number of turns": out.simu.machine.stator.winding.Ntcoil,
        "Stator winding and core temperature [degC]": out.simu.elec.Tsta,
        "Rotor magnet temperature [degC]": out.simu.elec.Trot,
        "d-axis line to neutral voltage [V"
        + dq_str
        + "]": dq_factor * out.elec.eec.OP.Ud_ref,
        "q-axis line to neutral voltage [V"
        + dq_str
        + "]": dq_factor * out.elec.eec.OP.Uq_ref,
        "d-axis line current [A" + dq_str + "]": dq_factor * out.elec.eec.OP.Id_ref,
        "q-axis line current [A" + dq_str + "]": dq_factor * out.elec.eec.OP.Iq_ref,
        "Line current [Arms]": Irms,
        "Line to line emf [Vrms]": np.sqrt(3) * Erms,
        "Line to line voltage (spec) [Vrms]": np.sqrt(3) * Vrms,
        "Line to line voltage (FEA) [Vrms]": np.sqrt(3) * Vrms_fea,
        "Phase Voltage Total Harmonic Distortion (THD) [%]": V_THD,
        "Current Total Harmonic Distortion (THD) [%]": I_THD,
        "Power factor [%]": power_factor,
        # "Phase shift Voltage/Current [deg]": V_out_I_out_phase_shift,
        "DC line resistance (MotorCAD) [Ohm]": out.simu.elec.eec.R1,
        "d-axis PM flux [Wb" + dq_str + "]": dq_factor * out.elec.eec.Phid_mag,
        "d-axis line inductance [µH]": out.elec.eec.Ld * 1e6,
        "q-axis line inductance [µH]": out.elec.eec.Lq * 1e6,
        "Switching frequency [Hz]": fswi,
        "Modulation index": M_I,
        "Constant ke1 : RPM vs voltage  [rpm/V]": ke_1,
        "Constant ke2 : Voltage vs speed [Vs/rad]": ke_2,
        "Constant kt : Torque vs current [Nm/A]": kt,
    }

    if np.abs(out.mag.Tem_av) > 1e-10:
        Tem_av = out.mag.Tem_av * 1e3
        Tem_rip_pp = out.mag.Tem_rip_pp * 1e3
        Tem_rip_norm = 100 * out.mag.Tem_rip_norm
    else:
        Tem_av = 0
        Tem_rip_pp = 0
        Tem_rip_norm = 0

    mag_val_dict = {
        "Electromagnetic average torque [mNm]": Tem_av,
        "Electromagnetic torque ripple [mNm]": Tem_rip_pp,
        "Electromagnetic torque ripple [%]": Tem_rip_norm,
    }

    loss_dt, loss_ms, loss_val_dict = comp_loss(out, is_print=False)

    losses = loss_val_dict["Overall losses [W]"]

    # Calculate efficiency: 100 - 100*losses/power
    if np.abs(active_power) > 1e-6:
        if active_power > 0:
            output_power = active_power - losses
            efficiency = 100 - 100 * losses / active_power
        else:
            output_power = active_power + losses
            efficiency = 100 - 100 * losses / np.abs(active_power)
    else:
        output_power = 0
        efficiency = 0

    loss_val_dict["Input power [W]"] = active_power

    loss_val_dict["Output power [W]"] = output_power

    loss_val_dict["Efficiency [%]"] = efficiency

    return elec_val_dict, mag_val_dict, loss_val_dict, loss_dt, loss_ms
