import numpy as np


def comp_loss_windage(out, sleeve_thickness=0, is_neon=False):

    machine = out.simu.machine

    OP = out.elec.OP
    felec = OP.get_felec()

    Dr = (machine.rotor.Rext + sleeve_thickness) * 2
    L = machine.rotor.L1
    p = machine.get_pole_pair_number()
    if is_neon:
        rho = 0.751  # neon density cf MotorCAD
        mu = 3.207e-5  # Dynamic viscosity of air
    else:
        rho = 1.225  # air density
        mu = 18.5e-6  # Dynamic viscosity of air
    k = 1
    omega = 2 * np.pi / p * felec
    delta = machine.comp_length_airgap_active() - sleeve_thickness

    # Couette Reynolds number
    Re_delta = rho * omega * Dr * delta / (2 * mu)

    if Re_delta < 64:
        C_M = 10 * (2 * delta / Dr) ** 0.3 / Re_delta
    elif Re_delta < 5e2:
        C_M = 2 * (2 * delta / Dr) ** 0.3 / Re_delta**0.6
    elif Re_delta < 1e4:
        C_M = 1.03 * (2 * delta / Dr) ** 0.3 / Re_delta**0.5
    else:
        C_M = 0.065 * (2 * delta / Dr) ** 0.3 / Re_delta**0.2

    P1 = 1 / 32 * k * C_M * np.pi * rho * omega**3 * Dr**4 * L

    Dri = machine.rotor.Rint

    # tip Reynolds number
    Re_r = rho * omega * Dr**2 / (4 * mu)

    if Re_r < 3e5:
        C_M = 3.87 / Re_r**0.5
    else:
        C_M = 0.146 / Re_r**0.2

    P2 = 1 / 64 * C_M * rho * omega**3 * (Dr**5 - Dri**5)

    Nt = out.elec.axes_dict["time"].get_length()

    Pwindage = (P1 + P2) * np.ones(Nt)

    meshsol = out.mag.meshsolution
    Igrp = meshsol.group["airgap"]
    Se_all = meshsol.mesh.get_element_area()
    Nelem = Se_all.size
    Se = Se_all[Igrp]

    # Compute the loss density for each element
    Pwindage_density = np.zeros((Nt, Nelem))
    Pwindage_density[:, Igrp] = Pwindage[:, None] / Se.sum()

    return Pwindage, Pwindage_density
