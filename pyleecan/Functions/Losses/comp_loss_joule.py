import numpy as np

from SciDataTool import DataTime


def comp_loss_joule(out, is_data=False):

    if (
        out.simu.elec is not None
        and out.simu.elec.eec is not None
        and out.simu.elec.eec.R1 is not None
    ):
        Rs = out.simu.elec.eec.R1
    else:
        Rs = 0

    Is = out.elec.get_Is()

    Is_val = Is.get_along("time", "phase[]")[Is.symbol]

    Pjoule = Rs * np.sum(Is_val**2, axis=1)

    meshsol = out.mag.meshsolution
    Igrp = meshsol.group["stator winding"]
    Se_all = meshsol.mesh.get_element_area()
    Nelem = Se_all.size
    Se = Se_all[Igrp]

    Pjoule_density = np.zeros((Is_val.shape[0], Nelem))
    Pjoule_density[:, Igrp] = Pjoule[:, None] / Se.sum()

    if is_data:
        Pjoule_data = DataTime(
            name="Stator winding Joule losses",
            symbol="L",
            unit="W",
            values=Pjoule,
            axes=[Is.axes[0].get_axis_periodic(Nper=1)],
        )
        return Pjoule_data, Pjoule_density
    else:
        return Pjoule, Pjoule_density
