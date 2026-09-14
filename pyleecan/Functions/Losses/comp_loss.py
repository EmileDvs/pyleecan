import numpy as np

from SciDataTool import DataTime, Data1D


from pyleecan.Classes.MeshSolution import MeshSolution
from pyleecan.Classes.SolutionData import SolutionData

from losses.comp_loss_core import comp_loss_core
from losses.comp_loss_proximity import comp_loss_proximity
from losses.comp_loss_magnet import comp_loss_magnet
from losses.comp_loss_joule import comp_loss_joule
from losses.comp_loss_windage import comp_loss_windage


def comp_loss(out, is_print=True):

    Pcore, Pcore_hys, Pcore_edd, Pcore_exc, Pcore_density = comp_loss_core(
        out, is_data=False
    )

    Pprox, Pprox_density = comp_loss_proximity(out, is_data=False)

    Pmagnet, Pmagnet_density = comp_loss_magnet(out, is_data=False)

    Pjoule, Pjoule_density = comp_loss_joule(out, is_data=False)

    Pwindage, Pwindage_density = comp_loss_windage(
        out, is_neon=True, sleeve_thickness=1.05e-3
    )

    Poverall = Pjoule + Pcore + Pprox + Pwindage + Pmagnet

    Time = out.mag.axes_dict["time"].get_axis_periodic(Nper=1)

    Ploss_data = DataTime(
        name="Motor losses",
        symbol="L",
        unit="W",
        values=np.hstack(
            (
                Poverall[:, None],
                Pjoule[:, None],
                Pcore[:, None],
                Pcore_hys[:, None],
                Pcore_edd[:, None],
                Pcore_exc[:, None],
                Pprox[:, None],
                Pwindage[:, None],
                Pmagnet[:, None],
            )
        ),
        axes=[
            Time,
            Data1D(
                name="Type",
                unit=" ",
                values=[
                    "Overall losses",
                    "Stator winding Joule losses",
                    "Stator core losses",
                    "Stator core hysteresis",
                    "Stator core eddy current",
                    "Stator core excess",
                    "Stator winding proximity losses",
                    "Airgap windage losses",
                    "Rotor magnet losses",
                ],
                is_components=True,
                is_overlay=True,
                filter={"Type": []},
            ),
        ],
    )

    ms_mag = out.mag.meshsolution
    axes_dict = out.loss.axes_dict

    loss_density = (
        Pcore_density
        + Pprox_density
        + Pmagnet_density
        + Pjoule_density
        + Pwindage_density
    )

    Loss_density_dt = DataTime(
        name=f"Overall loss density",
        unit="W/m3",
        symbol="L",
        values=loss_density,
        is_real=True,
        axes=[Time, axes_dict["indice"]],
    )

    Loss_density_sd = SolutionData(
        label=Loss_density_dt.name,
        field=Loss_density_dt,
        unit=Loss_density_dt.unit,
    )

    ms_loss = MeshSolution(
        label=Loss_density_sd.label,
        group={Loss_density_sd.label: Loss_density_sd},
        mesh=ms_mag.mesh,
        solution_dict={Loss_density_sd.label: Loss_density_sd},
        dimension=2,
    )

    if is_print:
        txt1 = f"""Stator winding joule loss (time-domain) : {Pjoule.mean():10.10f} [W]
    Stator core loss (time-domain) : {Pcore.mean():10.10f} [W]
    Stator winding proximity loss (time-domain) : {Pprox.mean():10.10f} [W]
    Airgap windage loss : {Pwindage.mean():10.10f} [W]
    Rotor magnet loss (time-domain) : {Pmagnet.mean():10.10f} [W]"""
        print(txt1)

        return Ploss_data, ms_loss

    else:

        Ploss_dict = {
            "Stator winding joule losses [W]": Pjoule.mean(),
            "Stator core losses [W]": Pcore.mean(),
            "Stator winding proximity losses [W]": Pprox.mean(),
            "Airgap windage losses [W]": Pwindage.mean(),
            "Rotor magnet losses [W]": Pmagnet.mean(),
        }
        Ploss_dict["Overall losses [W]"] = sum(Ploss_dict.values())
        Ploss_dict["Stator core hysteresis [W]"] = Pcore_hys.mean()
        Ploss_dict["Stator core eddy current [W]"] = Pcore_edd.mean()
        Ploss_dict["Stator core excess [W]"] = Pcore_exc.mean()

        return Ploss_data, ms_loss, Ploss_dict
