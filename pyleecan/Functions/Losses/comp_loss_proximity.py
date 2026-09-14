import numpy as np

from SciDataTool import DataTime


def comp_loss_proximity(out, is_data=True):

    machine = out.simu.machine

    per_a = 2
    Lst = machine.stator.L1

    # Proximity loss coefficient [W/m3]
    k_p = out.simu.loss.model_dict["proximity"].k_p / (4 * np.pi**2)

    meshsol = out.mag.meshsolution
    Igrp = meshsol.group["stator winding"]
    Se_all = meshsol.mesh.get_element_area()
    Nelem = Se_all.size
    Se = Se_all[Igrp]
    Bvect = meshsol["B"].field

    # Compute magnetic flux density derivative over time
    dB_dt_v = Bvect.get_vectorfield_along("time=derivate", "indice", "z")
    dB_dt = dB_dt_v.get_xyz_along("time", "indice=" + str(Igrp), "z=mean")

    # Compute the loss density for each element
    Pprox_density = np.zeros((dB_dt["comp_x"].shape[0], Nelem))
    Pprox_density[:, Igrp] = k_p * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)

    Pprox = Lst * per_a * np.matmul(Pprox_density[:, Igrp], Se)

    if is_data:
        Pprox_data = DataTime(
            name="Stator winding proximity losses",
            symbol="L",
            unit="W",
            values=Pprox,
            axes=[Bvect.components["comp_x"].axes[0].get_axis_periodic(Nper=1)],
        )

        return Pprox_data, Pprox_density
    else:
        return Pprox, Pprox_density
