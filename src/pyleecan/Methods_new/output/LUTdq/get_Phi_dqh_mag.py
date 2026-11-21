from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND


def get_Phi_dqh_mag(self) -> DataND:
    """Get magnet flux linkage over time in DQH frame

    Parameters
    ----------
    self : LUTdq
        a LUTdq object

    Returns
    ----------
    Phi_dqh_mag : DataND
        magnets flux linkage in dqh frame (Nt_tot, 3)
    """

    if self.Phi_dqh_mag is None:
        # Find Id=Iq=0
        ii = self.get_index_open_circuit()

        if ii is not None:
            stator_label = self.simu.machine.stator.get_label()

            phase_dir = self.output_list[ii].elec.phase_dir

            # Integrate stator winding flux contained in LUT over z
            Phi_wind0 = (
                self.output_list[ii]
                .mag.Phi_wind_slice[stator_label]
                .get_data_along("time", "phase", "z=integrate")
            )

            # dqh transform
            Phi_dqh_mag = Phi_wind0.n2dqh(
                is_dqh_rms=True,
                phase_dir=phase_dir,
            )

            # Store for next call
            self.Phi_dqh_mag = Phi_dqh_mag

    return self.Phi_dqh_mag
