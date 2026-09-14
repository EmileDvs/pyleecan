import numpy as np

from SciDataTool import Data1D, DataTime


def comp_loss_core(out, is_data=True):

    machine = out.simu.machine

    per_a = 2
    Lst = machine.stator.L1
    Kf = 1.0  # machine.stator.Kf1
    rho = machine.stator.mat_type.struct.rho
    k_ed = out.simu.loss.model_dict["stator core"].k_ed
    k_ex = out.simu.loss.model_dict["stator core"].k_ex
    beta = 2  # B exponent in hysteresis loss model

    meshsol = out.mag.meshsolution
    Igrp = meshsol.group["stator core"]
    Se_all = meshsol.mesh.get_element_area()
    Nelem = Se_all.size
    Se = Se_all[Igrp]
    Bvect = meshsol["B"].field
    Hvect = meshsol["H"].field
    H = Hvect.get_xyz_along("time", "indice=" + str(Igrp), "z=mean")

    # Compute magnetic flux density derivative over time
    dB_dt_v = Bvect.get_vectorfield_along("time=derivate", "indice", "z")
    dB_dt = dB_dt_v.get_xyz_along("time", "indice=" + str(Igrp), "z=mean")

    # Compute the loss density for each element and each frequency
    Pcore_density_hys = (
        np.abs(H["comp_x"] * dB_dt["comp_x"]) ** (2 / beta)
        + np.abs(H["comp_y"] * dB_dt["comp_y"]) ** (2 / beta)
    ) ** (beta / 2)

    Pcore_density_edd = (
        1
        / (2 * np.pi**2)
        * k_ed
        / Kf
        * rho
        * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)
    )

    Pcore_density_exc = (
        k_ex
        / Kf
        * rho
        / 8.763363
        * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2) ** 0.75
    )

    Pcore_hys = Lst * per_a * np.matmul(Pcore_density_hys, Se)
    Pcore_edd = Lst * per_a * np.matmul(Pcore_density_edd, Se)
    Pcore_exc = Lst * per_a * np.matmul(Pcore_density_exc, Se)

    Pcore = Pcore_hys + Pcore_edd + Pcore_exc

    Pcore_density = np.zeros((Pcore.size, Nelem))
    Pcore_density[:, Igrp] = Pcore_density_hys + Pcore_density_edd + Pcore_density_exc

    if is_data:
        Pcore_data = DataTime(
            name="Stator core losses",
            symbol="L",
            unit="W",
            values=np.hstack(
                (
                    Pcore[:, None],
                    Pcore_hys[:, None],
                    Pcore_edd[:, None],
                    Pcore_exc[:, None],
                )
            ),
            axes=[
                Bvect.components["comp_x"].axes[0].get_axis_periodic(Nper=1),
                Data1D(
                    name="type",
                    unit=" ",
                    values=["Overall", "Hysteresis", "Eddy current", "Excess"],
                    is_components=True,
                    is_overlay=True,
                    filter={"Phase": []},
                ),
            ],
        )

        return Pcore_data, Pcore_density
    else:
        return Pcore, Pcore_hys, Pcore_edd, Pcore_exc, Pcore_density
