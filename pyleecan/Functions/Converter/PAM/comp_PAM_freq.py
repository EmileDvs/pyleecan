import numpy as np

from SciDataTool import DataTime, Data1D, DataLinspace, Norm_ref, DataFreq

from pyleecan.Functions.Electrical.dqh_transformation_freq import (
    dqh2n_DataFreq,
    n2dqh_DataFreq,
)

from pyleecan.Functions.Electrical.dqh_transformation import (
    dqh2n_DataTime,
    n2dqh_DataTime,
)

from pam.comp_trapezoid import comp_trapezoid


def comp_PAM_freq(
    eec,
    bemf,
    I0,
    machine,
    is_skin_effect_resistance_fund=False,
    is_skin_effect_inductance=False,
    phase_dir=-1,
    current_dir=-1,
    felec=50,
    is_umc=True,
):

    if is_umc:
        print("Calculating PAM current and voltage with celeroton method")
    else:
        print("Calculating PAM current and voltage with classic 6-step method")

    Nt = bemf.axes[0].get_length()

    U0 = bemf.get_magnitude_along("freqs", "phase[]")[bemf.symbol][1] / np.sqrt(2)
    phi0 = bemf.get_phase_along("freqs", "phase[]")[bemf.symbol][1]

    # Calculating unit voltage, current and switch values for 3-phases accounting for phase given by phi0
    Ua_unit, Ia_unit, triga = comp_trapezoid(
        Nt=Nt, phase=phi0[0], current_dir=current_dir, N=10
    )
    Ub_unit, Ib_unit, trigb = comp_trapezoid(
        Nt=Nt, phase=phi0[1], current_dir=current_dir, N=10
    )
    Uc_unit, Ic_unit, trigc = comp_trapezoid(
        Nt=Nt, phase=phi0[2], current_dir=current_dir, N=10
    )

    # Calculating common mode (zero if not requested)
    Umc = is_umc * (Ua_unit + Ub_unit + Uc_unit) / 3

    # Calculating voltage with requested amplitude
    fft_Ua_unit = np.fft.rfft(Ua_unit - Umc)
    fft_Ua_unit /= Nt / 2
    fft_Ub_unit = np.fft.rfft(Ub_unit - Umc)
    fft_Ub_unit /= Nt / 2
    fft_Uc_unit = np.fft.rfft(Uc_unit - Umc)
    fft_Uc_unit /= Nt / 2

    funda = np.abs(fft_Ua_unit[1])
    fundb = np.abs(fft_Ub_unit[1])
    fundc = np.abs(fft_Uc_unit[1])

    Ua = np.sqrt(2) * U0[0] / funda * (Ua_unit - Umc)
    Ub = np.sqrt(2) * U0[1] / fundb * (Ub_unit - Umc)
    Uc = np.sqrt(2) * U0[2] / fundc * (Uc_unit - Umc)

    # Calculating current with requested amplitude
    t = bemf.axes[0].get_values()
    freqs = np.fft.rfftfreq(Nt, d=t[1] - t[0])
    fft_Ia_unit = np.fft.rfft(Ia_unit)
    fft_Ia_unit /= Nt / 2
    fft_Ib_unit = np.fft.rfft(Ib_unit)
    fft_Ib_unit /= Nt / 2
    fft_Ic_unit = np.fft.rfft(Ic_unit)
    fft_Ic_unit /= Nt / 2

    funda = np.abs(fft_Ia_unit[1])
    fundb = np.abs(fft_Ib_unit[1])
    fundc = np.abs(fft_Ic_unit[1])

    Ia = np.sqrt(2) * I0 / funda * Ia_unit
    Ib = np.sqrt(2) * I0 / fundb * Ib_unit
    Ic = np.sqrt(2) * I0 / fundc * Ic_unit

    # Creating the data object
    Phase_S = Data1D(
        name="phase",
        unit="rad",
        values=["A", "B", "C"],
        is_components=True,
        is_overlay=True,
        filter={"Phase": []},
    )

    Phase_unit = Data1D(
        name="phase",
        unit="rad",
        values=["A", "B", "C", "common mode"],
        is_components=True,
        is_overlay=True,
        filter={"Phase": []},
    )

    Time = DataLinspace(
        name="time",
        unit="s",
        initial=0,
        final=1 / felec,
        number=Nt,
        include_endpoint=False,
        normalizations={
            "elec_order": Norm_ref(ref=felec),
            "mech_order": Norm_ref(ref=felec),
            "angle_elec": Norm_ref(ref=current_dir / (2 * np.pi * felec)),
        },
    )

    Us = DataTime(
        name="Stator voltage",
        unit="V",
        symbol="U_s",
        axes=[Time, Phase_S],
        values=np.hstack((Ua[:, None], Ub[:, None], Uc[:, None])),
    )

    Is = DataFreq(
        name="Stator current",
        unit="A",
        symbol="I_s",
        axes=[Time, Phase_S],
        values=np.hstack((Ia[:, None], Ib[:, None], Ic[:, None])),
    )

    Trig = DataTime(
        name="Phase commutation",
        unit="V",
        symbol="C_s",
        axes=[Time, Phase_S],
        values=np.hstack((triga[:, None], trigb[:, None], trigc[:, None])),
    )

    U_unit = DataTime(
        name="Unit phase voltage",
        unit="V",
        symbol="U_{unit}",
        axes=[Time, Phase_unit],
        values=np.hstack(
            (Ua_unit[:, None], Ub_unit[:, None], Uc_unit[:, None], Umc[:, None])
        ),
    )

    I_unit = DataTime(
        name="Unit phase current DC",
        unit="V",
        symbol="Idc_{unit}",
        axes=[Time, Phase_S],
        values=np.hstack((Ia_unit[:, None], Ib_unit[:, None], Ic_unit[:, None])),
    )

    # Us.plot_2D_Data("time", "phase[0]", data_list=[bemf, Trig])
    # Us.plot_2D_Data("time", "phase[1]", data_list=[bemf, Trig])
    # Us.plot_2D_Data("time", "phase[2]", data_list=[bemf, Trig])

    # Is.plot_2D_Data("time", "phase[]")
    # Is.plot_2D_Data("freqs", "phase[]")

    # I_unit.plot_2D_Data("freqs", "phase[]")

    # Us_fund = Us.get_along("freqs[1]", "phase")[Us.symbol]
    # bemf_fund = bemf.get_along("freqs[1]", "phase")[bemf.symbol]

    # U_unit.plot_2D_Data("time", "phase[0]", data_list=[I_unit])

    # Is_t = Is.get_data_along(
    #     "time=axis_data",
    #     "phase[]",
    #     axis_data={"time": bemf.axes[0].get_values()},
    # )

    # Is_t.plot_2D_Data("time=derivate", "phase[]")

    # Trig.plot_2D_Data("time", "phase[]")

    # Get stator winding phase number
    qs = machine.stator.winding.qs

    # Get PAM frequencies in abc frame
    t = Us.axes[0].get_values()
    freqs_n = np.fft.rfftfreq(t.size, d=t[1] - t[0])

    Us_harm = Us.copy()
    Us_harm.values = Us.values - bemf.values

    # Us.plot_2D_Data("freqs", "phase[]")
    # bemf.plot_2D_Data("freqs", "phase[]")

    # Us_harm.plot_2D_Data("time", "phase[]")
    # Us_harm.plot_2D_Data("freqs", "phase[]")

    # Get stator voltage harmonics in dqh frame
    # Us_PWM = output.elec.get_Us(is_dqh=True, is_harm_only=True, is_freq=True)
    # Us_dqh = n2dqh_DataTime(Us_harm, phase_dir=phase_dir)
    Us_dqh_freq = n2dqh_DataFreq(
        Us_harm,
        is_dqh_rms=True,
        phase_dir=phase_dir,
        current_dir=current_dir,
        felec=felec,
    )
    result = Us_dqh_freq.get_along("freqs", "phase")
    Udqh_val = result[Us_dqh_freq.symbol]
    freqs_dqh = result["freqs"]

    # # Plot Us_n and U_dqh
    # output.elec.Us.plot_2D_Data("freqs", "phase[0]")
    # Us_PWM.plot_2D_Data("freqs=[0,200]", "phase[0]")
    # Us_dqh_freq.plot_2D_Data("freqs", "phase[2]", data_list=[Us_dqh])

    # Filter Udqh_val zeros values
    Udqh_norm = np.linalg.norm(Udqh_val, axis=-1)
    Iamp = Udqh_norm > 1e-6 * Udqh_norm.max()
    freqs_dqh = freqs_dqh[Iamp]
    Udqh_val = Udqh_val[Iamp, :]
    freqs_dqh[0] = 0

    # Init current harmonics matrix
    Idqh_val = np.zeros((freqs_dqh.size, qs), dtype=complex)

    # Look for frequency value in n frame for each frequency in dqh frame
    fn_dqh = np.zeros(freqs_dqh.size)
    fn_pos = freqs_dqh + felec
    fn_neg = freqs_dqh - felec
    for ii, (fpos, fneg) in enumerate(zip(fn_pos, fn_neg)):
        fn_ii = None
        jj = 0
        while fn_ii is None and jj < freqs_n.size:
            if np.abs(fpos - freqs_n[jj]) < 1e-4 or np.abs(fneg - freqs_n[jj]) < 1e-4:
                fn_ii = freqs_n[jj]
            elif np.abs(fpos + freqs_n[jj]) < 1e-4 or np.abs(fneg + freqs_n[jj]) < 1e-4:
                fn_ii = -freqs_n[jj]
            else:
                jj += 1
        if fn_ii is None:
            raise Exception("Cannot map dqh frequency back to n frequency")
        else:
            fn_dqh[ii] = fn_ii

    fn_dqh[np.abs(fn_dqh) < felec] = felec

    Nharm = fn_dqh.size

    if eec.type_skin_effect:
        CondS = machine.stator.winding.conductor
        # Calculate skin effect coefficient on stator resistance
        Xkr_skinS = CondS.comp_skin_effect_resistance(
            freq=fn_dqh, T_op=eec.Tsta, T_ref=20
        )
        if not is_skin_effect_resistance_fund:
            Xkr_skinS[fn_dqh == felec] = 1
        Xkr_skinS = Xkr_skinS.astype(complex)
        if is_skin_effect_inductance:
            # Calculate skin effect coefficient on stator inductances
            Xke_skinS = CondS.comp_skin_effect_inductance(
                freq=fn_dqh, T_op=eec.Tsta, T_ref=20
            )
        else:
            Xke_skinS = 1
    else:
        Xkr_skinS = np.ones(Nharm, dtype=complex)
        Xke_skinS = 1

    # Calculate impedances to solve linear system for all frequencies
    Nharm = fn_dqh.size
    we = 2 * np.pi * felec
    wh = 2 * np.pi * fn_dqh
    a = eec.R1 * Xkr_skinS
    a[1:] += 1j * wh[1:] * eec.Ld * Xke_skinS
    b = np.zeros(Nharm, dtype=complex)
    b[0] = -we * eec.Lq * Xke_skinS
    c = np.zeros(Nharm, dtype=complex)
    c[0] = we * eec.Ld * Xke_skinS
    d = eec.R1 * Xkr_skinS
    d[1:] += 1j * wh[1:] * eec.Lq * Xke_skinS
    det = a * d - c * b

    Edqh_val = np.zeros((Nharm, 3), dtype=complex)
    # Edqh_val[0, 0:2] = np.array([-we * eec.Phiq_mag, we * eec.Phid_mag])

    Y = Udqh_val - Edqh_val

    # Calculate current harmonics
    # Calculate Id
    Idqh_val[:, 0] = (d * Y[:, 0] - b * Y[:, 1]) / det
    # Calculate Iq
    Idqh_val[:, 1] = (-c * Y[:, 0] + a * Y[:, 1]) / det
    # Calculate Ih
    e = eec.R1 * Xkr_skinS
    e[1:] += 1j * wh[1:] * eec.Ld * Xke_skinS
    Idqh_val[:, 2] = Udqh_val[:, 2] / e

    # Create frequency axis
    Freqs_PWM = Us_dqh_freq.axes[0]

    norm_freq = dict()
    if Freqs_PWM.normalizations is not None and len(Freqs_PWM.normalizations) > 0:
        for key, val in Freqs_PWM.normalizations.items():
            norm_freq[key] = val.copy()

    Freqs = Data1D(
        name=Freqs_PWM.name,
        symbol=Freqs_PWM.symbol,
        unit=Freqs_PWM.unit,
        values=freqs_dqh,
        normalizations=norm_freq,
    )

    # Create DataFreq in DQH Frame
    Is_PAM_dqh = DataFreq(
        name="Stator current",
        unit="A",
        symbol="I_s",
        axes=[Freqs, Us_dqh_freq.axes[1].copy()],
        values=Idqh_val,
    )

    # # Plot PAM current in dqh frame over frequency
    # Is_PAM_dqh.plot_2D_Data("freqs", "phase[]")

    Is_PAM_dqh1 = Is_PAM_dqh.get_data_along(
        "time=axis_data",
        "phase[]",
        axis_data={"time": Us.axes[0].get_values()},
    )

    # Convert I_dqh spectrum back to stator frame
    Is_PAM_n = dqh2n_DataTime(Is_PAM_dqh1, n=qs, phase_dir=phase_dir)

    # Merge PAM harmonics with DC pulses
    Is_PAM_n.values += Is.values

    # Is_PAM_n.plot_2D_Data("time", "phase[]")
    # Is_PAM_n.plot_2D_Data("freqs", "phase[]")

    # Windowing signal
    Is_PAM_n1 = Is_PAM_n.get_data_along(
        "time=axis_data",
        "phase[]",
        axis_data={"time": Us.axes[0].get_values()},
    )

    Is_PAM_n1.values *= Trig.values

    # Is_PAM_n1.plot_2D_Data("time", "phase[]", data_list=[Is_PAM_n])

    # Remove current discontinuity by filtering high harmonic content
    Is_PAM_n2 = Is_PAM_n1.get_data_along("freqs", "phase[]")
    freqs = Is_PAM_n2.axes[0].get_values()
    wc = 50 * np.pi * felec
    RL_filter = 1 / np.sqrt(1 + (2 * np.pi * freqs / wc) ** 2)
    RL_filter /= RL_filter[1]

    Is_PAM_n2.values *= RL_filter[:, None]

    Is_PAM_n3 = Is_PAM_n2.get_data_along(
        "time=axis_data",
        "phase[]",
        axis_data={"time": Us.axes[0].get_values()},
    )

    # Is_PAM_n3.plot_2D_Data(
    #     "time", "phase[0]", data_list=[Is_PAM_n, Is_PAM_n1], legend_list=["3", "0", "1"]
    # )

    # Is_PAM_n3.plot_2D_Data(
    #     "freqs", "phase[0]", data_list=[Is_PAM_n, Is_PAM_n1], legend_list=["3", "0", "1"]
    # )

    return Is_PAM_n3, Us, Is, Trig, U_unit, I_unit
