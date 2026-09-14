import numpy as np

from SciDataTool import DataTime, Data1D, DataLinspace, Norm_ref, DataFreq

from pyleecan.Functions.Electrical.dqh_transformation_freq import (
    dqh2n_DataFreq,
    n2dqh_DataFreq,
)

from comp_trapezoid import comp_trapezoid


from scipy.integrate import solve_ivp


def comp_PAM_6step(
    eec,
    bemf,
    I0,
    machine,
    is_skin_effect_resistance_fund=False,
    is_skin_effect_inductance=False,
    phase_dir=-1,
    current_dir=-1,
    felec=50,
    Lh=0,
):
    """NOT WORKING"""

    print("Calculating PAM current and voltage with classic 6-step method")

    Nt = bemf.axes[0].get_length()

    U0 = bemf.get_magnitude_along("freqs", "phase[]")[bemf.symbol][1] / np.sqrt(2)
    phi0 = bemf.get_phase_along("freqs", "phase[]")[bemf.symbol][1]

    Ua_unit, Ia_unit, triga = comp_trapezoid(
        Nt=Nt, phase=phi0[0], current_dir=current_dir, N=10
    )
    Ub_unit, Ib_unit, trigb = comp_trapezoid(
        Nt=Nt, phase=phi0[1], current_dir=current_dir, N=10
    )
    Uc_unit, Ic_unit, trigc = comp_trapezoid(
        Nt=Nt, phase=phi0[2], current_dir=current_dir, N=10
    )

    fft_Ua_unit = np.fft.rfft(Ua_unit)
    fft_Ua_unit /= Nt / 2

    fft_Ub_unit = np.fft.rfft(Ub_unit)
    fft_Ub_unit /= Nt / 2

    fft_Uc_unit = np.fft.rfft(Uc_unit)
    fft_Uc_unit /= Nt / 2

    funda = np.abs(fft_Ua_unit[1])
    fundb = np.abs(fft_Ub_unit[1])
    fundc = np.abs(fft_Uc_unit[1])

    Ua = np.sqrt(2) * U0[0] / funda * Ua_unit
    Ub = np.sqrt(2) * U0[1] / fundb * Ub_unit
    Uc = np.sqrt(2) * U0[2] / fundc * Uc_unit

    Us_val = np.hstack((Ua[:, None], Ub[:, None], Uc[:, None]))
    trig = np.hstack((triga[:, None], trigb[:, None], trigc[:, None]))
    E_val = bemf.get_along("time", "phase[]")[bemf.symbol]

    V = Us_val - E_val
    t_vect = np.linspace(0, 1 / felec, Nt, endpoint=False)
    t_eval = np.linspace(0, 1000 / felec, 1000 * Nt, endpoint=False)

    def f(t, y, V, t_vect, felec):

        if t > t_vect[-1]:
            t_mod = np.mod(t, 1 / felec)
            # print(t_mod)
        else:
            t_mod = t

        I0 = np.where(t_vect == t_mod)[0]

        if I0.size > 0:
            V_i = V[I0[0], :]
        else:
            I0 = np.where(t_vect < t_mod)[0][-1]
            if I0 < t_vect.size - 1:
                tp = t_vect[[I0, I0 + 1]]
                Vp = V[[I0, I0 + 1], :]
            else:
                tp = [t_vect[I0], 1 / felec]
                Vp = V[[I0, 0], :]

            V_a = np.interp(t_mod, tp, Vp[:, 0])
            V_b = np.interp(t_mod, tp, Vp[:, 1])
            V_c = np.interp(t_mod, tp, Vp[:, 2])
            V_i = np.array([V_a, V_b, V_c])

        return -eec.R1 / eec.Ld * y + 1 / eec.Ld * V_i

    ode_res = solve_ivp(
        f,
        args=(V, t_vect, felec),
        t_span=[0, t_eval[-1]],
        y0=[0, 0, 0],
        t_eval=t_eval,
    )

    Is_val = ode_res.y.T

    # Creating the data object
    Phase_S = Data1D(
        name="phase",
        unit="rad",
        values=["A", "B", "C"],
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

    # Time2 = Data1D(
    #     name="time",
    #     unit="s",
    #     values=np.mod(t_eval[-600:], 1 / felec),
    #     normalizations={
    #         "elec_order": Norm_ref(ref=felec),
    #         "mech_order": Norm_ref(ref=felec),
    #         "angle_elec": Norm_ref(ref=current_dir / (2 * np.pi * felec)),
    #     },
    # )

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
        values=Is_val[-600:],
    )

    Trig = DataTime(
        name="Phase commutation",
        unit="V",
        symbol="C_s",
        axes=[Time, Phase_S],
        values=np.hstack((triga[:, None], trigb[:, None], trigc[:, None])),
    )

    V_data = DataTime(
        name="Diff voltage",
        unit="V",
        symbol="U_{unit}",
        axes=[Time, Phase_S],
        values=V,
    )

    I_unit = DataTime(
        name="Unit phase current DC",
        unit="V",
        symbol="Idc_{unit}",
        axes=[Time, Phase_S],
        values=np.hstack((Ia_unit[:, None], Ib_unit[:, None], Ic_unit[:, None])),
    )

    Us.plot_2D_Data("time", "phase[0]", data_list=[bemf])
    # Us.plot_2D_Data("time", "phase[1]", data_list=[bemf, Trig])
    # Us.plot_2D_Data("time", "phase[2]", data_list=[bemf, Trig])

    Is.plot_2D_Data("time", "phase[]")
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

    # Get stator voltage harmonics in dqh frame
    Us_dqh_freq = n2dqh_DataFreq(
        Us,
        is_dqh_rms=True,
        phase_dir=phase_dir,
        current_dir=current_dir,
        felec=felec,
    )
    result = Us_dqh_freq.get_along("freqs", "phase")
    Udqh_val = result[Us_dqh_freq.symbol]
    freqs_dqh = result["freqs"]

    # # Plot Us_n and U_dqh
    Us.plot_2D_Data("freqs", "phase[0]")
    # Us_PWM.plot_2D_Data("freqs=[0,200]", "phase[0]")
    Us_dqh_freq.plot_2D_Data("freqs", "phase[0,1,2]")

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
            Xkr_skinS[0] = 1
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
    Edqh_val[0, 0:2] = np.array([-we * eec.Phiq_mag, we * eec.Phid_mag])

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
    Is_PAM_dqh.plot_2D_Data("freqs", "phase[]")

    # Convert I_dqh spectrum back to stator frame
    Is_PAM_n = dqh2n_DataFreq(
        Is_PAM_dqh,
        n=qs,
        phase_dir=phase_dir,
        current_dir=current_dir,
        felec=felec,
        is_n_rms=False,
    )

    # Reduce current to original voltage frequencies
    Is_PAM_n1 = Is_PAM_n.get_data_along("freqs=" + str(freqs_n.tolist()), "phase")

    if np.max(np.abs(Is_PAM_n1.axes[0].get_values() - Is.axes[0].values)) < 1e-6:
        Is_PAM_n1.values += Is.values
    else:
        raise Exception("Cannot merge current spectrum")

    # Is_PAM_n1.plot_2D_Data("freqs", "phase[]")

    # Is_PAM_n1.plot_2D_Data(
    #     "time=axis_data",
    #     "phase[0,1,2]",
    #     axis_data={"time": Us.axes[0].get_values()},
    # )

    # Windowing signal
    # Is_PAM_n2 = Is_PAM_n1.get_data_along(
    #     "time=axis_data",
    #     "phase[0,1,2]",
    #     axis_data={"time": Us.axes[0].get_values()},
    # )

    # Is_PAM_n2.values *= Trig.values

    return Is_PAM_n1, Us, Is, Trig, U_unit, I_unit
