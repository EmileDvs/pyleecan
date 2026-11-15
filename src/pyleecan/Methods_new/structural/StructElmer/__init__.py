# -*- coding: utf-8 -*-
from os.path import join
import subprocess

from ....Functions.get_path_binary import get_path_binary
from ....Functions.labels import (
    AIRBOX_R_LAB,
    AIRBOX_SR_LAB,
    SHAFTSR_LAB,
    SHAFTSL_LAB,
    YSR_LAB,
    YSL_LAB,
    ROTOR_LAB,
    STATOR_LAB,
    SBS_TR_LAB,
    SBS_TL_LAB,
    SBS_BR_LAB,
    SBS_BL_LAB,
    SBR_B_LAB,
    SBR_T_LAB,
    AS_TR_LAB,
    AS_TL_LAB,
    AS_BR_LAB,
    AS_BL_LAB,
    AR_T_LAB,
    AIRBOX_SL_LAB,
    AIRBOX_SR_LAB,
    AIRBOX_R_LAB,
    LAM_LAB,
    BORE_LAB,
)


class ElmerProcessError(Exception):
    """Raised when there is an Elmer Binary process error"""

    pass


def _execute(binary_name, cwd, logger, parameter=None):
    """Function to execute Elmer Binaries in the current working directory 'cwd'"""
    # Elmer must be installed and in the PATH
    binary = get_path_binary(binary_name)

    cmd = ['"' + binary + '"']
    logger.info(f"Calling {binary_name}: " + " ".join(map(str, cmd)))

    if parameter:
        cmd.extend(parameter)

    popen = subprocess.Popen(
        " ".join(cmd),
        stdout=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
        cwd=cwd,
    )

    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise ElmerProcessError(
            f"Elmer Process Error while executing {' '.join(cmd)}: Return Code [{return_code}]"
        )


def _get_BP_dict():
    """Build the mapping of Pyleecan labels to structural Elmer boundaries."""
    rotor_label = ROTOR_LAB + "-0_"
    stator_label = STATOR_LAB + "-0_"
    return {
        AS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
        AS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
        SBS_BR_LAB: "MASTER_ROTOR_BOUNDARY",
        SBS_BL_LAB: "SLAVE_ROTOR_BOUNDARY",
        SBR_B_LAB: "SB_ROTOR_BOUNDARY",
        rotor_label + LAM_LAB + BORE_LAB: "ROTOR_BORE_CURVE",
        rotor_label + YSR_LAB: "MASTER_ROTOR_BOUNDARY",
        rotor_label + YSL_LAB: "SLAVE_ROTOR_BOUNDARY",
        stator_label + YSR_LAB: "MASTER_STATOR_BOUNDARY",
        stator_label + YSL_LAB: "SLAVE_STATOR_BOUNDARY",
        SHAFTSR_LAB: "MASTER_ROTOR_BOUNDARY",
        SHAFTSL_LAB: "SLAVE_ROTOR_BOUNDARY",
        AIRBOX_R_LAB: "VP0_BOUNDARY",
        AIRBOX_SR_LAB: "MASTER_STATOR_BOUNDARY",
        AIRBOX_SL_LAB: "SLAVE_STATOR_BOUNDARY",
        AS_TR_LAB: "MASTER_STATOR_BOUNDARY",
        AS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
        AR_T_LAB: "AIRGAP_ARC_BOUNDARY",
        SBS_TR_LAB: "MASTER_STATOR_BOUNDARY",
        SBS_TL_LAB: "SLAVE_STATOR_BOUNDARY",
        SBR_T_LAB: "SB_STATOR_BOUNDARY",
    }


StructElmer_BP_dict = _get_BP_dict()


# List of all StructElmer Boundary conditions
StructElmer_BP_list = list(set(StructElmer_BP_dict.values()))
