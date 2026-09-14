import numpy as np

from SciDataTool import DataTime


def comp_loss_magnet(out, is_data=True):

    machine = out.simu.machine

    per_a = 2
    Lst = machine.rotor.L1

    magnet = machine.rotor.magnet

    meshsol = out.mag.meshsolution
    Igrp = meshsol.group["rotor magnets"]

    Se_all = meshsol.mesh.get_element_area()
    Nelem = Se_all.size
    Se = Se_all[Igrp]

    Az = meshsol["A_z^{element}"].field.get_data_along(
        "time[smallestperiod]", "indice=" + str(Igrp), "z=mean"
    )

    # Check Time axis periodicity in function of group
    if "antiperiod" in Az.axes[0].symmetries:
        Az.axes[0].symmetries = {"period": Az.axes[0].symmetries["antiperiod"]}

    sigma_m = magnet.mat_type.elec.get_conductivity(T_op=out.simu.loss.Trot)

    # Compute magnetic flux density derivative over time
    dAz_dt = Az.get_data_along("time=derivate", "indice", "z")
    dAz_dt_val = dAz_dt.get_along("time", "indice", "z=mean")[dAz_dt.symbol]

    Jm = -sigma_m * dAz_dt_val
    Jc = np.matmul(Jm, Se)[:, None] / Se.sum()
    Jm -= Jc

    Pmagnet_density = np.zeros((dAz_dt_val.shape[0], Nelem))
    Pmagnet_density[:, Igrp] = 0.5 * Jm**2 / sigma_m

    Pmagnet = Lst * per_a * np.matmul(Pmagnet_density[:, Igrp], Se)

    if is_data:
        Pmagnet_data = DataTime(
            name="Rotor magnet losses",
            symbol="L",
            unit="W",
            values=Pmagnet,
            axes=[Az.axes[0].get_axis_periodic(Nper=1)],
        )

        return Pmagnet_data, Pmagnet_density
    else:
        return Pmagnet, Pmagnet_density
