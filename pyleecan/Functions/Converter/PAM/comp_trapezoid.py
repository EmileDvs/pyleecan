import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def comp_trapezoid(
    Nt=501,
    width=2.0,
    slope=3,
    amp=1.0,
    offs=-0.5,
    phase=0,
    current_dir=-1,
    N=10,
):

    t = np.linspace(0, 2, Nt, endpoint=False)

    a = np.round(
        slope * width * signal.sawtooth(2 * np.pi * t / width, width=0.5) / 4.0, 6
    )

    I0_1 = np.zeros(Nt)
    I0_1[a > amp / 2.0] = current_dir * amp / 2.0
    I0_1[a < -amp / 2.0] = -current_dir * amp / 2.0

    I0_2 = np.zeros(Nt)
    I0_2[a >= amp / 2.0] = current_dir * amp / 2.0
    I0_2[a <= -amp / 2.0] = -current_dir * amp / 2.0

    I0 = 0.5 * (I0_1 + I0_2)

    ii = np.where(np.abs(I0) == 0.25)[0]
    x = np.arange(0, 2 * N + 1)
    for jj in ii:
        I0[jj - N : jj + N + 1] = np.interp(x, [0, 2 * N], [I0[jj - 1], I0[jj + 1]])

    trig0 = np.array(np.abs(I0) > 0, dtype=int)

    a[a > amp / 2.0] = amp / 2.0
    a[a < -amp / 2.0] = -amp / 2.0
    sig0 = current_dir * 2.0 * (a + amp / 2.0 + offs)

    # plt.figure()
    # plt.plot(t, sig0)
    # plt.plot(t, I0)
    # plt.plot(t, I1, "r--")

    # fft_sig0 = np.fft.rfft(sig0)
    # fft_trig0 = np.fft.rfft(trig0)
    # freq = np.fft.rfftfreq(t.size, d=t[1] - t[0])

    # plt.figure()
    # plt.bar(freq[:100], np.abs(fft_sig0[:100]), width=1)

    # phase0 = np.angle(fft_sig0[1])

    # fft_sig1 = np.exp(-1j * current_dir * 2 * freq * phase) * fft_sig0

    # sig1 = np.fft.irfft(fft_sig1, n=t.size)

    # fft_trig1 = np.exp(1j * 2 * freq * phase) * fft_trig0
    # trig1 = np.fft.irfft(fft_trig1, n=t.size)

    Nroll = current_dir * int(np.round(phase / (2 * np.pi) * trig0.size))
    sig1 = np.roll(sig0, Nroll)
    trig2 = np.roll(trig0, Nroll)
    I1 = np.roll(I0, Nroll)

    # plt.figure()
    # plt.plot(t, sig0)
    # # plt.plot(t, trig0, "g--")
    # # plt.plot(t, trig1, "r--")
    # plt.plot(t, trig0, "y")
    # plt.plot(t, I0, "k--")

    # plt.figure()
    # plt.plot(t, sig1)
    # # plt.plot(t, trig0, "g--")
    # # plt.plot(t, trig1, "r--")
    # plt.plot(t, trig2, "y")
    # plt.plot(t, I1, "k--")
    # # plt.show()

    return sig1, I1, trig2
