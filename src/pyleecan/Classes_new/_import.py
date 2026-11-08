"""Generated class imports; do not edit by hand."""

from importlib import import_module

from ._error import InitUnKnowClassError

_CLASS_MODULES = {'Arc': 'arc', 'Arc1': 'arc_1', 'Arc2': 'arc_2', 'Arc3': 'arc_3', 'Bore': 'bore', 'BoreFlower': 'bore_flower', 'BoreLSRPM': 'bore_lsrpm', 'BoreSinePole': 'bore_sine_pole', 'BoreUD': 'bore_ud', 'Circle': 'circle', 'CondType11': 'cond_type_11', 'CondType12': 'cond_type_12', 'CondType13': 'cond_type_13', 'CondType21': 'cond_type_21', 'CondType22': 'cond_type_22', 'Conductor': 'conductor', 'Convert': 'convert', 'ConvertMC': 'convert_mc', 'DXFImport': 'dxf_import', 'Data': 'data', 'Data1D': 'data_1d', 'DataDual': 'data_dual', 'DataFreq': 'data_freq', 'DataKeeper': 'data_keeper', 'DataLinspace': 'data_linspace', 'DataND': 'data_nd', 'DataPattern': 'data_pattern', 'DataTime': 'data_time', 'Drive': 'drive', 'DriveWave': 'drive_wave', 'EEC': 'eec', 'EEC_LSRPM': 'eec_lsrpm', 'EEC_PMSM': 'eec_pmsm', 'EEC_SCIM': 'eec_scim', 'ElecLUTdq': 'elec_lut_dq', 'Electrical': 'electrical', 'ElementMat': 'element_mat', 'Elmer': 'elmer', 'ElmerResults': 'elmer_results', 'ElmerResultsVTU': 'elmer_results_vtu', 'EndWinding': 'end_winding', 'EndWindingCirc': 'end_winding_circ', 'EndWindingRect': 'end_winding_rect', 'FPGNSeg': 'fpgn_seg', 'FPGNTri': 'fpgn_tri', 'Force': 'force', 'ForceMT': 'force_mt', 'ForceTensor': 'force_tensor', 'Frame': 'frame', 'FrameBar': 'frame_bar', 'GUIOption': 'gui_option', 'GaussPoint': 'gauss_point', 'Hole': 'hole', 'HoleM50': 'hole_m_50', 'HoleM51': 'hole_m_51', 'HoleM52': 'hole_m_52', 'HoleM52R': 'hole_m_52_r', 'HoleM53': 'hole_m_53', 'HoleM54': 'hole_m_54', 'HoleM57': 'hole_m_57', 'HoleM58': 'hole_m_58', 'HoleM60': 'hole_m_60', 'HoleM61': 'hole_m_61', 'HoleM62': 'hole_m_62', 'HoleM63': 'hole_m_63', 'HoleMLSRPM': 'hole_mlsrpm', 'HoleMag': 'hole_mag', 'HoleUD': 'hole_ud', 'Import': 'import_', 'ImportData': 'import_data', 'ImportGenMatrixSin': 'import_gen_matrix_sin', 'ImportGenPWM': 'import_gen_pwm', 'ImportGenToothSaw': 'import_gen_tooth_saw', 'ImportGenVectLin': 'import_gen_vect_lin', 'ImportGenVectSin': 'import_gen_vect_sin', 'ImportMatlab': 'import_matlab', 'ImportMatrix': 'import_matrix', 'ImportMatrixVal': 'import_matrix_val', 'ImportMatrixXls': 'import_matrix_xls', 'ImportMeshMat': 'import_mesh_mat', 'ImportMeshUnv': 'import_mesh_unv', 'ImportVectorField': 'import_vector_field', 'Input': 'input', 'InputCurrent': 'input_current', 'InputFlux': 'input_flux', 'InputForce': 'input_force', 'InputVoltage': 'input_voltage', 'LUT': 'lut', 'LUTdq': 'lut_dq', 'LUTslip': 'lut_slip', 'LamH': 'lam_h', 'LamHole': 'lam_hole', 'LamHoleNS': 'lam_hole_ns', 'LamSlot': 'lam_slot', 'LamSlotM': 'lam_slot_m', 'LamSlotMag': 'lam_slot_mag', 'LamSlotMagNS': 'lam_slot_mag_ns', 'LamSlotMulti': 'lam_slot_multi', 'LamSlotMultiWind': 'lam_slot_multi_wind', 'LamSlotWind': 'lam_slot_wind', 'LamSquirrelCage': 'lam_squirrel_cage', 'LamSquirrelCageMag': 'lam_squirrel_cage_mag', 'Lamination': 'lamination', 'Line': 'line', 'Loss': 'loss', 'LossFEA': 'loss_fea', 'LossModel': 'loss_model', 'LossModelBertotti': 'loss_model_bertotti', 'LossModelJoule': 'loss_model_joule', 'LossModelMagnet': 'loss_model_magnet', 'LossModelProximity': 'loss_model_proximity', 'LossModelSteinmetz': 'loss_model_steinmetz', 'LossModelWindagePyrhonen': 'loss_model_windage_pyrhonen', 'LossModelWinding': 'loss_model_winding', 'Machine': 'machine', 'MachineAsync': 'machine_async', 'MachineDFIM': 'machine_dfim', 'MachineIPMSM': 'machine_ipmsm', 'MachineLSPM': 'machine_lspm', 'MachineSCIM': 'machine_scim', 'MachineSIPMSM': 'machine_sipmsm', 'MachineSRM': 'machine_srm', 'MachineSyRM': 'machine_sy_rm', 'MachineSync': 'machine_sync', 'MachineUD': 'machine_ud', 'MachineWRSM': 'machine_wrsm', 'MagElmer': 'mag_elmer', 'MagFEMM': 'mag_femm', 'Magnet': 'magnet', 'Magnetics': 'magnetics', 'MatEconomical': 'mat_economical', 'MatElectrical': 'mat_electrical', 'MatHT': 'mat_ht', 'MatMagnetics': 'mat_magnetics', 'MatStructural': 'mat_structural', 'Material': 'material', 'Mesh': 'mesh', 'MeshMat': 'mesh_mat', 'MeshSolution': 'mesh_solution', 'MeshVTK': 'mesh_vtk', 'Mode': 'mode', 'ModelBH': 'model_bh', 'ModelBH_Langevin': 'model_bh_langevin', 'ModelBH_arctangent': 'model_bh_arctangent', 'ModelBH_exponential': 'model_bh_exponential', 'ModelBH_linear_sat': 'model_bh_linear_sat', 'NodeMat': 'node_mat', 'NormAffine': 'norm_affine', 'NormFunc': 'norm_func', 'NormIndices': 'norm_indices', 'NormRef': 'norm_ref', 'NormVector': 'norm_vector', 'Normalization': 'normalization', 'Notch': 'notch', 'NotchEvenDist': 'notch_even_dist', 'OP': 'op', 'OPMatrix': 'op_matrix', 'OPdq': 'op_dq', 'OPdqf': 'op_dqf', 'OPslip': 'op_slip', 'OptiBayesAlg': 'opti_bayes_alg', 'OptiBayesAlgSmoot': 'opti_bayes_alg_smoot', 'OptiConstraint': 'opti_constraint', 'OptiDesignVar': 'opti_design_var', 'OptiDesignVarInterval': 'opti_design_var_interval', 'OptiDesignVarSet': 'opti_design_var_set', 'OptiGenAlg': 'opti_gen_alg', 'OptiGenAlgNsga2Deap': 'opti_gen_alg_nsga_2_deap', 'OptiObjective': 'opti_objective', 'OptiProblem': 'opti_problem', 'OptiSolver': 'opti_solver', 'OutElec': 'out_elec', 'OutForce': 'out_force', 'OutGeo': 'out_geo', 'OutGeoLam': 'out_geo_lam', 'OutInternal': 'out_internal', 'OutLoss': 'out_loss', 'OutLossModel': 'out_loss_model', 'OutMag': 'out_mag', 'OutMagElmer': 'out_mag_elmer', 'OutMagFEMM': 'out_mag_femm', 'OutPost': 'out_post', 'OutStruct': 'out_struct', 'Output': 'output', 'ParamExplorer': 'param_explorer', 'ParamExplorerInterval': 'param_explorer_interval', 'ParamExplorerSet': 'param_explorer_set', 'PolarArc': 'polar_arc', 'Post': 'post', 'PostFunction': 'post_function', 'PostLUT': 'post_lut', 'PostMethod': 'post_method', 'PostPlot': 'post_plot', 'RefElement': 'ref_element', 'RefLine3': 'ref_line_3', 'RefQuad4': 'ref_quad_4', 'RefQuad9': 'ref_quad_9', 'RefSegmentP1': 'ref_segment_p_1', 'RefTriangle3': 'ref_triangle_3', 'RefTriangle6': 'ref_triangle_6', 'RequestedAxis': 'requested_axis', 'Rule': 'rule', 'RuleComplex': 'rule_complex', 'RuleEquation': 'rule_equation', 'RuleSimple': 'rule_simple', 'ScalarProduct': 'scalar_product', 'ScalarProductL2': 'scalar_product_l2', 'Section': 'section', 'Segment': 'segment', 'Shaft': 'shaft', 'Simu1': 'simu_1', 'Simulation': 'simulation', 'Skew': 'skew', 'SliceModel': 'slice_model', 'Slot': 'slot', 'Slot19': 'slot_19', 'SlotCirc': 'slot_circ', 'SlotDC': 'slot_dc', 'SlotM10': 'slot_m_10', 'SlotM11': 'slot_m_11', 'SlotM12': 'slot_m_12', 'SlotM13': 'slot_m_13', 'SlotM14': 'slot_m_14', 'SlotM15': 'slot_m_15', 'SlotM16': 'slot_m_16', 'SlotM17': 'slot_m_17', 'SlotM18': 'slot_m_18', 'SlotM18_2': 'slot_m_18_2', 'SlotM19': 'slot_m_19', 'SlotUD': 'slot_ud', 'SlotUD2': 'slot_ud_2', 'SlotW10': 'slot_w_10', 'SlotW11': 'slot_w_11', 'SlotW11_2': 'slot_w_11_2', 'SlotW12': 'slot_w_12', 'SlotW13': 'slot_w_13', 'SlotW14': 'slot_w_14', 'SlotW15': 'slot_w_15', 'SlotW16': 'slot_w_16', 'SlotW21': 'slot_w_21', 'SlotW22': 'slot_w_22', 'SlotW23': 'slot_w_23', 'SlotW24': 'slot_w_24', 'SlotW25': 'slot_w_25', 'SlotW26': 'slot_w_26', 'SlotW27': 'slot_w_27', 'SlotW28': 'slot_w_28', 'SlotW29': 'slot_w_29', 'SlotW30': 'slot_w_30', 'SlotW60': 'slot_w_60', 'SlotW61': 'slot_w_61', 'SlotW62': 'slot_w_62', 'SlotW63': 'slot_w_63', 'SlotWLSRPM': 'slot_wlsrpm', 'Solution': 'solution', 'SolutionData': 'solution_data', 'SolutionMat': 'solution_mat', 'SolutionVector': 'solution_vector', 'SolverInputFile': 'solver_input_file', 'StructElmer': 'struct_elmer', 'Structural': 'structural', 'SurfLine': 'surf_line', 'SurfRing': 'surf_ring', 'Surface': 'surface', 'Trapeze': 'trapeze', 'Unit': 'unit', 'VarLoad': 'var_load', 'VarLoadCurrent': 'var_load_current', 'VarLoadVoltage': 'var_load_voltage', 'VarOpti': 'var_opti', 'VarParam': 'var_param', 'VarParamSweep': 'var_param_sweep', 'VarSimu': 'var_simu', 'VectorField': 'vector_field', 'VentilationCirc': 'ventilation_circ', 'VentilationPolar': 'ventilation_polar', 'VentilationTrap': 'ventilation_trap', 'Winding': 'winding', 'WindingSC': 'winding_sc', 'WindingUD': 'winding_ud', 'XOutput': 'xoutput'}
_LEGACY_NAMES = {'Norm_affine': 'NormAffine', 'Norm_func': 'NormFunc', 'Norm_indices': 'NormIndices', 'Norm_ref': 'NormRef', 'Norm_vector': 'NormVector'}
__all__ = ["import_class", *_CLASS_MODULES]


def import_class(class_name, prop_name=""):
    """Import a generated class by name."""
    class_name = _LEGACY_NAMES.get(class_name, class_name)
    module_name = _CLASS_MODULES.get(class_name)
    if module_name is None:
        message = "Unknow class name " + str(class_name)
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message)
    target = __package__ + "." + module_name
    try:
        module = import_module(target)
    except ModuleNotFoundError as error:
        if error.name != target:
            raise
        message = "Unknow class name " + class_name
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message) from error
    try:
        return getattr(module, class_name)
    except AttributeError as error:
        message = "Unknow class name " + class_name
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message) from error


def __getattr__(name):
    if name not in _CLASS_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = import_class(name)
    globals()[name] = value
    return value
