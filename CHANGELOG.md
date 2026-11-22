# Changelog

All notable changes to pyleecan are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The roadmap of the ongoing refactoring is in
[PLAN.md](PLAN.md), its detailed tasks in [BACKLOG.md](BACKLOG.md).

## [Unreleased]

Refactoring of the pyleecan classes onto standard Python class models
(branch `switch_to_dataclass`). The new implementations live next to the
legacy code (`Classes`, `Functions`, `Methods`), which is unchanged, and are
validated against it (Phase 1). The legacy code is removed in Phase 2.

### Added

- **New class generator** (`Generator/ClassGenerator/New/`): generates the
  classes from the legacy CSV definitions as standard Python classes, with
  methods inlined from the legacy `Methods` and snake_case module names
  (`LamSlotWind` -> `lam_slot_wind.py`).
- **`Classes_new`**: classes based on stdlib dataclasses (+ dacite for
  loading), on the `PyleecanClass` base.
- **`Classes_pydantic`**: the same classes as pydantic v2 models, on the
  `PyleecanModel` base. The class generator has a `backend` option
  (`"dataclass"` -> `Classes_new`, `"pydantic"` -> `Classes_pydantic`); both
  packages have the same class tree and share the vendored code of
  `Classes_new`. All 281 classes build and round-trip through
  `as_dict`/`from_dict`.
- **`Functions_new`**: copy of the legacy `Functions` targeting the new
  classes, with snake_case module names and the errors shared in
  `classes_common/errors.py`.
- **`Functions_pydantic`**: the new functions for the pydantic classes,
  generated from `Functions_new` by rewriting the imports only
  (`generate_function_pydantic.py`): one source for the function code. All 37
  machine files of `Data/Machine` load the same with the legacy, dataclass and
  pydantic `load`.
- **`Tests/New`**: copy of the legacy tests targeting the new classes and
  functions; test data gathered in `Tests/Data`. The tests import the classes
  and functions through alias packages (`backend_classes`,
  `backend_functions`): `pytest --backend=dataclass|pydantic` selects the
  implementation under test. The legacy class tests pass the same on both.
- **Cross tests** (`Tests/New/Cross`): for every class, the legacy, dataclass
  and pydantic implementations give the same legacy dictionary, load the
  legacy dictionaries and give the same JSON dump.
- **`ClassInfo`** (`Classes_new/_class_info.py`): the class information
  (properties, types, units, min/max, descriptions) is rebuilt at runtime from
  the classes themselves; `Class_Dict.json` is no longer needed.
- **Class sub-packages**: the classes of `Classes_new` are organized in
  lowercase sub-packages following the legacy packages (`geometry`, `machine`,
  `slot`, ...; `Import` becomes `import_data`). The `electrical` (with EEC and
  Drive), `magnetics`, `force` and `structural` (with Mode) modules and their
  child classes are taken out of `simulation`.
- **Target bases and legacy layer**: `PyleecanClass` (dataclass) and
  `PyleecanModel` (pydantic) are the Phase 2 design and share the pydantic
  API: `model_dump(mode="python"|"json")`, `model_validate` (polymorphic on
  `"__class__"`, unknown keys rejected), `model_copy` and an ndarray-aware
  `==`. The legacy behaviours (parent links, `None` and `-1` values, ignored
  unknown keys, `as_dict`/`from_dict`/`copy`/`compare`) are in `LegacyClass` /
  `LegacyModel`, which the generated classes derive from during Phase 1. A
  contract test suite checks both target bases with the same specification.
- **Validation of the dataclasses**: the type of every field and its bounds
  (min/max) are checked at construction and on assignment, with the same
  rules as the pydantic models (bool is not a number, an int is accepted for a
  float, list and dict items are checked, a dict builds the declared class).
  Errors are the shared `CheckTypeError`/`CheckMinError`/`CheckMaxError`.
- **Legacy value rules** in both legacy layers: None everywhere, integral float
  for an int field, function given by its source (lambda or path to a python
  file, saved by its source), file path or array for an object / ImportMatrix
  field, `-1` for the declared class.
- **Shared errors**: every method error is defined once in
  `classes_common/errors.py` (255 errors) and raised by both implementations;
  previously each class held its own nested copy.
- **`Methods_new`**: the methods of the new classes, written by a method
  generator (`generate_methods_new.py`) from the legacy `Methods` for all
  packages, self-contained and importable (new import names: `Classes_new`,
  `Functions_new`, shared errors), and read by the class generator. It
  gathers the method-level modernizations (shared with the functions
  generator: `source_names.py`); a package needing hand-written changes can
  be frozen.
- **Type hints** drafted from the numpydoc docstrings by the method generator
  (Geometry first: 125 of 164 parameters, 72 of 131 returns), with the class
  names imported under `if TYPE_CHECKING:`; `Methods_new` is checked with
  `ty`. Local containers passed to a container field are declared with the
  field type (`curve_list: list[Line] = list()`), and local dicts unpacked as
  keyword arguments as `dict[str, Any]` (Slot: 198 -> 20 `ty` diagnostics).
  Machine hinted (445/458 parameters, 321/337 returns), with rules for
  undocumented returns (`-> None`) and conventional parameters, unions
  (`X or Y`, Returns alternatives), `| None` for explicit `return None`.
  Simulation hinted (86/97 parameters, 82/90 returns). Loss hinted (8/8 parameters,
  16/16 returns). Output (100/123, 57/80) and Optimization (16/41,
  8/17) hinted. Converter hinted (77/95, 86/100).
  All the other packages of Methods_new hinted (first pass).
- **Loss models of #751** (merged from `loss_fea`), carried to both new
  implementations by the generators: frequency and time loss models
  (`comp_loss_freq`, `comp_loss_time`) for Bertotti, Steinmetz, Joule,
  proximity, magnet and windage losses, fitting plots, `LossFEA` with
  enforced and fitted coefficients, loss DataKeepers
  (`VarSimu.get_loss_datakeeper`), `OutLoss` input/output power,
  efficiency and torque; `OutMag.meshsolution` holds the stator and rotor
  frame solutions (`B_S`/`B_R`), merged by `OutMag.get_meshsolution()`.
- **Class-specific functions moved to their class**
  (`Generator/ClassGenerator/New/moved_functions.py`): `get_area` and
  `get_indices_limited` become methods of `MeshSolution`, `run_multisim_step`
  a static method of `VarSimu`. The old function paths of `Functions_new` and
  `Functions_pydantic` are deprecated aliases (`DeprecationWarning`) until
  Phase 2. The other functions used by a single class stay utilities.
- **Geometry utilities in `utils.geometry`** (Step 8): the intersection
  and circle helpers (`inter_line_circle`, `inter_line_line`,
  `inter_circle_circle`, `circle_from_3_points`, `comp_flower_arc`,
  `cut_lines_between_angle`, `comp_surface_num`) in one module; the old
  `Geometry.*` paths are deprecated aliases. `merge_notch_list` is a
  static method of `Lamination`, `transform_hole_surf` of `Hole`.
- **Plot helpers** (Step 8): `get_color_legend_from_surface` is a static
  method of `Machine` (the colors read from the configuration when
  called); `init_fig` is in `utils`, `set_plot_gui_icon` in the
  `Tools` of the GUI; the old paths are deprecated.
- **Root helpers in the `utils` package, `log_error` in the GUI** (Step 8):
  `labels`, `path_tools`, `init_environment`, `make_ndarray_equal` and
  `get_path_binary` are in `utils`, `log_error` in the `Tools.log_error`
  module of the GUI; the old `Functions` modules are deprecated and
  re-export the names (constants included).
- **Dead code deprecated** (Step 8): `Plot.Pyvista.get_arrows_plt`,
  `Geometry.create_surface`, `FEMM.comp_FEMM_Jcus`, `FEMM.create_FEMM_bar`,
  `getattr_recursive`, `short_filepath` warn (no caller; removed in
  Phase 2).
- **Converter rule functions from a static registry** (Step 8):
  `Converter.rule_functions` maps the rule names to their modules (no
  import by name); the complex rules work on both backends;
  `Converter.MotorCAD.slotW23_H1` is deprecated (not used).
- **GUI on the new classes** (Step 10, first pass): `GUI_new` (dataclass)
  and `GUI_pydantic` are generated from the legacy GUI (same modernization
  as the methods; the Qt resources shared with the legacy GUI).
- **Container arguments instead of parent reads** (Step 11, first pass):
  the slot surface methods (`get_surface_active`, `get_surface_opening`,
  `get_surface_wedges`, `comp_height_active`) take the lamination (or
  notch) as an optional `lam` argument, passed by the lamination; without
  it they fall back to the parent (`classes_common.parents.
  container_or_parent`, deprecated in Phase 2). The models' `run` take the
  simulation output (`run(output=None)`), passed by `Simu1.run_single`.
- **Loggers without the parent chain** (Step 9):
  `classes_common.logger_context.get_logger(obj)` gives the object's
  logger, else the logger of the simulation in progress
  (`Simulation.run` sets the context), else the default one; the methods
  and functions call it (`get_logger(self)`), `Functions.get_logger` is
  deprecated.
- **Utility functions refactored, group by group** (Step 8):
  - Optimization: `evaluate`, `check_cstr`, `tournamentDCD`, `update`
    become methods of `OptiGenAlgNsga2Deap` (the last two static);
  - Simulation: `get_elec_datakeeper_dict`, `log_datakeeper_step_result`
    become static methods of `VarSimu`;
  - Winding: the winding matrix transformations `reverse_wind_mat`,
    `reverse_layer`, `change_layer`, `permute_B_C`, `shift_wind_mat` and
    `find_wind_phase_color` become static methods of `Winding`;
    `get_phase_id` a regular method of `Winding` reading its connection
    matrix (`wind_mat` optional); `comp_cond_function` a static method
    of `Conductor`; `gen_phase_list` stays a utility;
  - the methods added to the classes and the interface objects have type
    hints (drafted from the docstrings, completed by overrides);
  - MeshSolution: `build_solution_data`, `build_solution_vector` become
    static constructors of `SolutionData` / `SolutionVector`,
    `get_frame_meshsolution` a method of `Output`; the deleted
    `build_meshsolution` stays a deprecated alias of the `MeshSolution`
    constructor;
  - `Structural.conversions` deprecated: its functions are in
    `SciDataTool.conversions` (`cart2pol_points`, `pol2cart_points`,
    `rphiz_to_xyz_3d` for the ones differing from the SciDataTool
    functions);
  - deprecated: `plot_2D_Data`, `plot_3D_Data` (use the `Data` methods),
    `comp_loss_joule` (not used), `DeprecationWarning` on each call;
  - dqh transformations: `DataTime.n2dqh`, `DataFreq.n2dqh` and
    `DataDual.n2dqh` (time data) replace `n2dqh_DataTime` /
    `n2dqh_DataFreq`, `DataTime.dqh2n` / `DataFreq.dqh2n` replace
    `dqh2n_DataTime` / `dqh2n_DataFreq`, `DataDual.dqh2n` (time data); the other functions are in one module,
    `SciDataTool.dqh_transformation` (frequency versions with a `_freq`
    suffix), without the checks of the data axes; the old paths are
    deprecated aliases;
  - `animate_as_gif` becomes a static method of `Data` (any plot of the
    Data objects; its VectorField branch used an undefined name, fixed);
  - `comp_MTPA` becomes a method of `LUTdq` (`LUT.comp_MTPA(machine,
    ...)`);
  - FEMM: the FEMM functions are the methods of one interface object,
    `femm_pyleecan` (`FEMM.femm_pyleecan`), holding the FEMM handler
    (`femm_pyleecan.handler`), one object per FEMM instance;
    `OutMagFEMM.handler_list` holds these objects; the old paths are
    deprecated aliases;
  - PyVista: the PyVista plot functions are the static methods of one
    object, `pv_plotter_pyleecan` (`Plot.Pyvista.pv_plotter_pyleecan`);
    the old paths are deprecated aliases;
  - GMSH: the gmsh functions are the static methods of one object,
    `gmsh_pyleecan` (`GMSH.gmsh_pyleecan`); the old paths are deprecated
    aliases;
  - the file retrocompatibility is shared by the backends in
    `classes_common.retrocompatibility` (`convert_init_dict` takes the
    class lookup of the backend); the `Load.retrocompatibility` modules
    of `Functions_new` / `Functions_pydantic` bind it to their classes.
  The old paths are deprecated aliases until Phase 2.
- **Class lookup by name** without generated table: `import_class` and
  `ClassInfo` walk the sub-packages.
- **`pyleecan.classes_common`**: support shared by the class implementations,
  independent of dataclasses or pydantic: class naming rules and lookup
  (`class_lookup`), `ClassInfo` (`class_info`), legacy checks (`check`),
  errors (`errors`, generated), parent rules (`parent_types`, generated) and
  the FEMM handler. One exception class per error, whatever the implementation
  that raises it. Each class package binds the lookup and `ClassInfo` to its
  own classes (`_import.py`, `_class_info.py`).

### Changed

- Generated classes use regular (function-local) imports for known class
  names instead of dynamic imports; `import_class` is kept for names known at
  runtime only (serialized `__class__`).
- Every generated class is built with keyword arguments in the new methods,
  functions and tests (pydantic models only accept keyword arguments).
- A legacy property starting with `_` (`Section._statements`, `_comments`)
  is, in pydantic models, a field without the `_` whose legacy name is kept as
  alias (files) and as a property (methods).
- `pydantic>=2.12` is a dependency.
- The legacy `compare` and `as_dict` of both implementations are shared
  (`classes_common`); `compare` reports the legacy paths (`name.list[0]`,
  `name.dict[key]`, `len(name.list)`).
- Loading a dataclass no longer type-checks with dacite: the fields are
  validated by the class itself.
- Pydantic `complex` fields use the native pydantic type (int, float and the
  string form accepted); the legacy string serialization is done by
  `LegacyModel.as_dict`.
- The new functions test `isinstance(obj, PyleecanBase)` (marker of both
  bases) instead of the dataclass base.
- The class bases save and log with the functions of their own backend
  (`Functions_new` / `Functions_pydantic`) instead of the legacy `Functions`.
- Class constants refactored to avoid circular imports; attribute metadata
  (unit, min, max) and descriptions follow the legacy definitions.
- The load function returns objects of the new classes.
- Normalization classes follow the class naming convention (`Norm_ref` ->
  `NormRef`); the legacy names remain accepted when loading files. The
  mapping is defined once in `classes_common.class_lookup`.
- The class generator no longer imports generated code (it read the legacy
  class names from the generated `Functions_new`).

- **GUI widget limits and help from the classes**: the `Gen_*` modules of
  `GUI_new` / `GUI_pydantic` (spinbox and float edit limits, tooltips) are
  written from `ClassInfo` instead of the CSV class definitions.
- **Unknown attributes rejected by the dataclass classes (legacy layer)**:
  as the legacy classes, `obj.unknown = 1` raises an `AttributeError` (it
  was accepted silently); an existing method can still be replaced.
- **Custom property setters of the simulation classes** (legacy layers):
  `ParamExplorer.setter` / `getter` and `DataKeeper.keeper` accept the
  legacy forms (callable, lambda source, path to a python file with a
  `<..._DIR>` wildcard, path in the simulation `"simu.machine..."`), saved
  by their source; `VarLoad.OP_matrix` accepts a matrix, a file or a dump.
- **Parent links only on the fields holding objects** (legacy layers), as
  the legacy setters: the objects of a plain list field
  (`ParamExplorerSet.value`) keep their own parent.
- **Validation errors of the pydantic classes (legacy layer)**: a rejected
  value raises the legacy errors (`CheckMinError`, `CheckMaxError`,
  `CheckTypeError`, same message as the legacy and dataclass classes; the
  pydantic `ValidationError` chained as `__cause__`), an unknown constructor
  argument a `TypeError`, an unknown attribute an `AttributeError`. The
  target base `PyleecanModel` keeps the pydantic `ValidationError`.

### Deprecated

- `LUTdq.comp_MTPA` (and the legacy path `Functions.Electrical.comp_MTPA`):
  written for an older equivalent circuit API, it does not run with the
  current one; it warns and is removed in Phase 2.

### Fixed

- **Legacy method bugs fixed in `Methods_new`** (`legacy_fixes.py`, applied
  by the method generator; the legacy `Methods` are unchanged). Only lines
  that always raised an exception change:
  - `VectorField.get_harm_xyz_along`: missing `pol2cart` import (NameError);
  - `EEC_SCIM._comp_flux_mean`: `n2abc` called with an unknown `n` argument
    (TypeError);
  - `DataND.compare_along`, `compare_magnitude_along`, `compare_phase_along`:
    `get_interpolation` called without the axis index (TypeError);
  - `ModelBH.fit_model`: smoothing without `Bmax` nor `Hmax` used undefined
    names (NameError), extrapolation to `Hmax` without `Bmax` used an unbound
    point count (UnboundLocalError);
  - `ConvertMC.convert_slot_to_other` / `convert_slot_rotor_to_other`:
    UnboundLocalError instead of the NotImplementedError of an unsupported
    slot;
  - `BoreSinePole.get_bore_line`: `raise ()` (TypeError) replaced by a
    `ValueError`;
  - `OP.get_OP_array` / `OPMatrix.get_OP_array` without arguments:
    AttributeError / IndexError instead of the default columns;
  - `ElecLUTdq.run` with loss models: `OutLoss` built with unknown fields
    (TypeError); the losses are stored in `OutLoss.loss_dict`.
  - `OutLossModel.get_mesh_solution` (`plot_mesh` of a loss model): the
    `indice` axis no longer exists since the OutMag mesh solution of #751
    (KeyError): the loss density is given on the `indice_element` axis, on
    the elements of the model's group, as `OutLoss.get_meshsolution`.
- **`LossFEA.run` with the new classes**: the overall loss added to
  `output.loss.loss_dict` was read back through the local dict, which the
  legacy classes stored as is; the new classes store a copy of an assigned
  dict (`ParentDict`), so the local name lacked it (`KeyError: 'overall'`).
  The local name is rebound to the stored dict (`legacy_fixes.py`).
- **Missing cases returning None** (Step 14, by hand in `Methods_new`):
  `LamSquirrelCage.plot_schematics_scr(is_default=True)` and
  `HoleM52R.plot_schematics` return `(fig, ax)` (the value of the plot was
  lost); `SlotW14` / `SlotW29` surfaces with a `wedge_type` other than 0
  and 1 raise `NotImplementedError`, `SlotW15.comp_surface_opening` on an
  inward slot raises `S15InnerError`, `HoleUD.comp_surface_magnet_id` on an
  index without magnet raises `ValueError` (all returned None).
- **SciDataTool plots** (`plot_2D`, `plot_3D`, `plot_4D`, fixed by the
  functions generator, `FUNCTION_LEGACY_FIXES`): a figure given without
  axes, or axes without figure, no longer fail; log scales on x / y
  (`Axes.xscale` did not exist) and the stem plots (`matplotlib.cm.get_cmap`,
  removed in matplotlib 3.9) work; `is_logscale_z` of the 3D plots no
  longer calls a missing `zscale` (the values are already in dB).
- **`n2dqh` without `phase_dir`** (SciDataTool dqh transformation): an
  explicit `ValueError` instead of a `TypeError` (the phase direction
  needs the current direction, which the values alone do not give).
- **`SurfLine.get_patches` without lines** returns `[]` (it built an empty
  `Polygon`, which raises `ValueError`, and returned it outside a list).
  `Surface.draw_FEMM` without `FEMM_dict` (or without `BC_dict` for a line
  with a boundary condition) raises a `ValueError` instead of a `TypeError`
  on None.
- Generation of the phase axis.
- **Upstream fixes carried to the new code** (#748, #749, #752): MagFEMM
  mesh extraction without a hardcoded Windows separator; MagElmer
  CalcFields solver with an explicit linear system (Elmer >= 26); numpy 2
  compatibility (2-D cross products in `Segment.comp_distance` and
  `ForceTensor.element_loop`, `load`).
- **PyVista plots**: the first plot of a process failed ("module 'pyvista'
  has no attribute 'plotting'"): the generated modules import the
  PyVista submodules loaded on demand.
- **Class generator**: a helper function imported from another method
  module of the class (`LossModelBertotti` / `LossModelSteinmetz`
  `comp_loss_val`, used by `comp_coeff` and `plot_fitting`) is a static
  method of the class instead of a runtime import of the method module;
  the helpers of a static method are called on the class (they were
  called on an undefined `self`).
- **Class generator**: a CSV description ending with a double quote
  produced an invalid attribute docstring (SyntaxError).
- **Functions generator**: a legacy function module deleted upstream no
  longer stays in `Functions_new` and `Functions_pydantic`.
- **GUI crashes on garbage collection** (access violation; the legacy GUI
  as well) in `GUI_new` / `GUI_pydantic`: `FloatEdit(parent)` took the
  parent as its unit, so the line edit was built without parent and deleted
  twice when its dialog was collected (`unit` is now keyword-only,
  `GUI_LEGACY_FIXES`); the replaced pages are hidden and deleted by Qt
  instead of being orphaned with `setParent(None)`. The GUI tests run in
  one process on both backends.
- **GUI generator**: the class created from the tree editor
  (`TreeEditContextMenu`) is a class of the backend, not a legacy class.
- **Functions generator**: no legacy import left in `Load/import_class`
  (`InitUnKnowClassError`) and `femm_pyleecan` (`NotImplementedYetError`):
  the shared errors.
- **User config file written only when it changes, atomically**
  (`Functions/init_environment.save_config_dict`). `import pyleecan.definitions`
  rewrote `main_config_dict.json` at each import: processes importing pyleecan
  at the same time could read a truncated file (`JSONDecodeError`). The file
  is now written only when its content changes, through a temporary file
  replacing it; its content is unchanged (same JSON format).
- **Class generator speed**: full regeneration ~220 s -> ~95 s, generated files
  unchanged. The method preparation is reused (errors search, both
  backends); the module maps are cached; the methods, class drafts and class
  finishing run in a process pool (`worker_pool.py`; threads were serialized
  by the GIL); Ruff runs once per step for all the classes instead of ~6
  processes per class.

### Status

Phase 1 progress (see [PLAN.md](PLAN.md)):

| Step | Status |
|---|---|
| 0. Separate the implementations in the generator | done |
| 1. Split the bases (target / legacy layer) | done |
| 2. Type, min and max validation for dataclasses | done |
| 3. `Functions_pydantic` | done |
| 4. Phase 1 test architecture (`--backend`) | done (method results compared at the freeze, Step 12) |
| 5. `Methods_new` generator and type hints, first pass | done for all packages; legacy bugs found by `ty` to fix |
| 6. Class-specific functions moved to their class | done (3 functions) |
| 7. Integrate the open legacy pull requests (#748, #749, #751, #752) | done |
| 8. Refactor the remaining `Functions` modules (generator) | done |
| 9. Logger chain (generator) | done |
| 10. GUI, first pass (generator) | in progress |
| 11. Parent links, first pass (generator) | in progress |
| 12. Freeze | to do |
| 13. Custom property setters and getters (frozen) | to do |
| 14. Type hints, second pass (frozen) | to do |
| 15. Utility functions (frozen) | to do |
| 16. Parent links, second pass (frozen) | to do |
| 17. GUI, second pass (frozen) | to do |
| 18. Backend comparison (benchmark) | to do |

Legacy class tests (`Tests/New/Classes`), with each backend: 2855 passed,
1 failed (`test_copy_out`: custom property setter of `ParamExplorer`, planned
in Step 13). Cross tests (`Tests/New/Cross`): 1405 passed.
