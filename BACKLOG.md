# Backlog of the class refactoring

Detailed tasks of the remaining steps of [PLAN.md](PLAN.md), with the findings
and the reference data they need. A task done is checked here and summarized
in the [CHANGELOG](CHANGELOG.md); the step checkbox of PLAN.md is checked
when all its tasks are done.

Modes: **generator** tasks change `Generator/ClassGenerator/New/` (never the
generated folders); **frozen** tasks edit `Methods_new` / `Functions_new` by
hand, after the freeze (Step 12).

## Step 5: legacy bugs

Found by `ty` on the first type hint pass. These lines raise an exception
when they run; they are fixed in the method generator (`legacy_fixes.py`,
`LEGACY_FIXES`: text replacements in the copies of the legacy modules, before
the modernization; a fix whose legacy text is not found stops the
generation), each listed under "Fixed" in the CHANGELOG. Fixes change the
behaviour against legacy only where legacy raised an error.

- [x] `VectorField.get_harm_xyz_along`: `pol2cart` not imported (NameError).
- [x] `EEC_SCIM._comp_flux_mean`: `n2abc(..., n=...)`, `n2abc` has no `n`
      parameter (TypeError); `n` is taken from the shape, argument removed.
- [x] `DataND.compare_along` / `compare_magnitude_along` /
      `compare_phase_along`: `get_interpolation` called without its `index`
      argument (TypeError). The index counts the axes left in each array
      (`get_along` squeezes the single-value axes, they are not interpolated).
      Extension axes (`"max"`, `"rms"`...) are still not handled (legacy limit).
- [x] `ModelBH.fit_model`: the last `else` branch calls `self.BH_func(H, Bs, a)`
      with undefined `Bs` and `a` (NameError), and `new_BH` is unbound there:
      smoothing with the fitted parameters. Also found: `Hmax` imposed without
      `Bmax` left `iteration` unbound; same 1% step as the `Bmax` extrapolation.
- [x] `ConvertMC.convert_slot_to_other` / `convert_slot_rotor_to_other`: the
      `else` branch builds its error message with `name_slot` before it is
      assigned (UnboundLocalError instead of NotImplementedError): the message
      gives the slot class.
- [x] `BoreSinePole.get_bore_line`: `raise ()` (TODO in the legacy code: a
      TypeError): `ValueError` with the number of intersections.
- [x] Checked (bug or `ty` limit):
  - `ElecLUTdq.run`: bug, `OutLoss` has no `Pjoule`... fields (TypeError when
    the LUT has loss models; still the case on `loss_fea`, #751). The losses
    go to `OutLoss.loss_dict`, one `OutLossModel` (`scalar_value`) per loss,
    named as in `LUTdq.interp_Ploss_dqh` (`joule`, `stator core`, `magnets`,
    `rotor core`, `proximity`). Reviewed with #751 (Step 7): the fix still
    applies; the loss names differ from `LossFEA.run` (open point of the
    #751 merge).
  - `OP.get_OP_array`: bug, `append` on the `*arg_list` tuple without
    arguments (AttributeError): converted to a list as in `OPMatrix`. Both
    `OP` and `OPMatrix` also sized `OP_matrix` before adding the default
    columns (IndexError): sized after.
  - `NotchEvenDist.get_notch_desc_list`: `ty` limit (value type of a dict
    mixing angles and objects).

## Step 6: class-specific functions

Rules: a legacy function moves into a class when it depends on that class's
meaning or data, not merely because a single class calls it today. A function
taking the object as first argument becomes a regular or private method;
`@staticmethod` only for functions that do not use the object. Heavy optional
dependencies (FEMM, gmsh, pyvista) stay imported inside the method. The old
path stays as a deprecated alias until Phase 2. SciDataTool internals are out
of scope.

Decision (2026-11-17, 17 modules used by a single class): moved `get_area`,
`get_indices_limited` (`MeshSolution`), `run_multisim_step` (`VarSimu`,
static). Kept as utilities: generic helpers (`circle_from_3_points`,
`comp_surface_num`, `cut_lines_between_angles`, `make_ndarray_equal`), FEMM
helpers working on the FEMM handler, not on `MagFEMM` (`comp_FEMM_torque`,
`comp_FEMM_Phi_wind`, `get_FEMM_BC_propname`), generic MeshSolution builders
(`build_meshsolution`, `build_solution_data`, `build_solution_vector`),
pyvista helpers (`plot_glyph_pv`, `plot_surf_deflection`), `get_path_binary`
(environment); `check_parent` goes with the parent links (Step 16). These
decisions may be revised by the per-module plan of Step 8.

## Step 7: integrate the open legacy pull requests

The legacy folders (`Classes`, `Methods`, `Functions`, the CSV files) are
never edited on this branch; they change only through these merges. The
generators then carry the changes to the new code.

- [x] #751 (branch `loss_fea`, last commit 694870ea4 "test_LossFEMM_Prius:
      update skew expected losses"): finished by the maintainer, except the
      time-domain core loss model (`comp_loss_time`, check commented in
      `test_LossFEMM_Prius`), left open.
- [x] #748: merge, regenerate, check (2026-11-21, with #749 and #752).
- [x] #749: merge, regenerate, check.
- [x] #751: merge, regenerate, check (2026-11-21, details below).
- [x] #752: merge, regenerate, check.

### #748, #749, #752 merge (2026-11-21)

The three pull requests are merged upstream (Eomys/pyleecan master
1e940df98, old layout). Through `loss_fea_src`: branch `upstream_old` =
`loss_fea` + upstream master (old layout, conflicts resolved there),
merged into `loss_fea_src`, then into `switch_to_dataclass`. `loss_fea`
itself is unchanged (it does not contain upstream master yet).

- #748 applies to `MagFEMM.get_FEMM_mesh_results` (`get_meshsolution`
  renamed by `loss_fea`); the `"\\mu"` labels of #752 kept with
  `mag.get_meshsolution()` in the FEMM meshsolution and parallelization
  tests.
- On this branch, the escapes of #752 were already fixed (raw strings,
  `/` in `path_tools`): kept; `setup.py` stays deleted.
- Regeneration: Segment, ForceTensor, MagElmer, MagFEMM, `load` and their
  tests only. The GUI change of #752 (`DMachineSetup`) has no new
  counterpart (GUI not migrated).

Checks: `Tests/Classes` 3937 passed; `Tests/New/Classes` 2855 passed and
`test_copy_out` failed with each backend; `Tests/New/Cross` 1405 passed;
`Tests/New/Methods` Geometry, Slot, Import, Simulation, Mesh: same failures
as before, plus `test_import_mesh_unv[unv_file0]` (below).
`ty`: geometry 21 -> 22, force 68, magnetics 159; force coverage 11/23,
5/10 (new `cross2d` helper of #752 not hinted).

- [ ] Generator bug (pre-existing): the pyvista import pass turns
      `from pyvista.plotting import Plotter` into `pv.plotting.Plotter` with
      `import pyvista as pv` only; pyvista 0.49 loads `pyvista.plotting`
      lazily (`AttributeError: module 'pyvista' has no attribute
      'plotting'`). The first plot of a process fails
      (`Functions_new/Plot/Pyvista/configure_plot.py`):
      `test_plot_contour_1group` before, `test_import_mesh_unv[unv_file0]`
      now that #752 fixed its file paths. Fix: also import the submodule
      (`import pyvista.plotting`) in `_apply_pyvista_import_style`.

### #751 merge (2026-11-21)

How the merge was done (to repeat for the next `loss_fea` commits):

- `loss_fea` still has the old layout (`pyleecan/`); a direct merge across
  the move to `src/pyleecan/` paired small CSV files wrongly (rename
  detection). The branch `loss_fea_src` holds `loss_fea` in the `src/`
  layout: merge of the move commit 1aa69709f with `-s ours` and the same
  `git mv pyleecan src/pyleecan`. `switch_to_dataclass` merges
  `loss_fea_src` (merge base: the move commit, no rename detection).
  Next `loss_fea` commits: merge `loss_fea` into `loss_fea_src` (pure
  rename, exact), then `loss_fea_src` into `switch_to_dataclass`.
- Six commits reverted on master before the move (Oct 30) are part of the
  pull request: `loss_fea` reverts three of them itself, and keeps the rotor
  mesh periodicity (3f077720b), `qs > 3` in `OutElec.get_electrical`
  (69db4c8e0) and the periodicity warning message (cc4c17888).
- Legacy side, resolved as the SciDataTool merge did: CSV types
  `SciDataTool.Classes.X.Y` written `Y`, `from SciDataTool import X`
  replaced by `Classes.X` imports (methods, functions,
  `Tests/Validation/Loss/test_loss_models.py`), CSV files normalized and
  legacy `Classes` regenerated by the legacy generator (black on `Classes`
  only); `requirements*.txt` removed (`ezdxf>=1.4.4` already in
  `pyproject.toml`); tutorials use `mag.get_meshsolution()`.
- Generator fixes found by the merge: a CSV description ending with `"`
  closed the attribute docstring (`LossFEA.type_loss_model_core`,
  `_attribute_docstring`); a legacy function module deleted upstream
  (`Functions/MeshSolution/build_meshsolution.py`) stayed in `Functions_new`
  and `Functions_pydantic` (`remove_stale_modules`; the hand-written modules
  of the freeze will have to be excluded, Step 12).

Checks: `Tests/Classes` 3937 passed; `Tests/New/Classes` 2855 passed and
`test_copy_out` failed with each backend (as before); `Tests/New/Cross` 1405
passed; `Tests/New/Methods/Simulation` and `Mesh`: same failures as before
the merge (`test_simu_get_OP_array`, `test_plot_contour_1group`, pydantic
`test_VarParamSweep_fct_save_load`); new `test_loss_models` 12 passed
(legacy and both backends); legacy `test_LossFEMM_Prius` passes.

Open points:

- [ ] `test_LossFEMM_Prius` (`Tests/New`, dataclass): `KeyError: 'overall'`
      in `LossFEA.run`. The legacy code assigns `output.loss.loss_dict =
      loss_dict`, then adds `"overall"` to `output.loss.loss_dict` and reads
      it from the local `loss_dict`: it relies on the setter keeping the same
      dict, the new classes validate and store a copy. To change on
      `loss_fea` (read `output.loss.loss_dict` after the assignment), not a
      legacy fix (legacy does not raise).
- [ ] Loss names: `LossFEA.run` and `VarSimu.get_loss_datakeeper` use
      `"stator joule"`, `"rotor magnets"`, `"stator proximity"`;
      `LUTdq.interp_Ploss_dqh` and the `ElecLUTdq.run` fix use `"joule"`,
      `"magnets"`, `"proximity"`. To align on `loss_fea`.
- [ ] `ty` diagnostics of the packages touched (Step 14 table): loss 11 ->
      64, magnetics 144 -> 159, output 81 -> 83, simulation 62 -> 73. No new
      legacy bug (Step 5 kind); known causes: `Machine.rotor`,
      `Data.get_values` / `get_length`, `Solution.field` not declared on the
      bases, optional fields, DataKeeper functions given as strings (Step 13),
      two Returns sections listing 2 values for 3 returned
      (`LossModelJoule.comp_loss_freq`, `LossModelWindagePyrhonen.comp_loss_freq`).

For each merge:

- conflicts resolved in the generators, never in the generated folders;
- new CSV classes placed in their sub-package (moved physics classes:
  `class_generator`), new legacy functions handled by the functions
  generator, new tests by the test generator;
- `Tests/Classes`, `Tests/New/Classes` (both backends), `Tests/New/Cross` and
  the method tests of the packages touched pass;
- `HINTED_SUBPACKAGES` coverage and `ty` diagnostics of the packages touched
  updated in the Step 14 table; new legacy bugs added to Step 5.

## Step 8: refactor the remaining `Functions` modules

Goal: drastically reduce the utility functions left for Phase 2. Each module
of `Functions` (outside SciDataTool and the vendored code) gets a target:
moved to a class (`MOVED_FUNCTIONS`), merged with another module, kept as a
utility (`utils/` in Phase 2), or removed (dead code, deprecated first).

- [x] Inventory (2026-11-21, below).
- [ ] Plan per module: decided with the maintainer, one group at a time
      (Decision column); each group done is listed in the CHANGELOG.
- [ ] Generator support for the targets the Step 6 mechanism does not cover
      yet (e.g. merging modules, functions moved together as a group).
- [ ] Apply the plan, one module or group per increment: deprecated aliases
      at the old paths, callers in `Methods_new` and `Functions_new` updated,
      test generator redirects, tests unchanged.
- [ ] Type hints drafted for the functions that stay utilities: run the
      `type_hints.py` pass in the functions generator (same rules as the
      methods), report the coverage and the `ty` diagnostics of
      `Functions_new`.

### Inventory

126 modules in `Functions` outside `SciDataTool`; 7 vendored (`_swat_em`,
`_smoot`, Phase 2 `_vendor/`) and 23 MotorCAD conversion rules (loaded by
name by `RuleComplex._set_fct_name`) are out of the per-module work: 96
modules to decide. Callers counted from the imports (AST) of the legacy
`Methods` (M), `Functions` (F), `GUI` (G), `Classes` (C) and `Tests` (T);
the classes are those of the calling methods. Already done in Step 6:
`MeshSolution.get_area`, `MeshSolution.get_indices_limited`,
`Simulation.VarSimu.run_multisim_step`; not copied: `copy`.

Targets: **class** (method of a class, `MOVED_FUNCTIONS`), **merge** (into
another module), **utility** (kept, `utils/` in Phase 2), **remove** (dead
code: deprecated alias in Phase 1, removed in Phase 2), **other step**.
Proposed targets are a starting point; the decision is the maintainer's.

| # | Group | Modules (callers) | Proposed target | Decision |
|---|---|---|---|---|
| 1 | Dead code | `Plot.plot_2D_Data`, `Plot.plot_3D_Data` (already deprecated), `Plot.animate_as_gif`, `Plot.Pyvista.get_arrows_plt`, `Geometry.create_surface`, `FEMM.comp_FEMM_Jcus`, `FEMM.create_FEMM_bar`, `Electrical.comp_MTPA`, `getattr_recursive`, `short_filepath`, `Converter.Utils.EquivalentError` (no caller) | remove | |
| 2 | Winding | `reverse_wind_mat`, `shift_wind_mat` (M6: Winding, WindingSC, WindingUD), `comp_cond_function` (M2: LamSlotWind, LamSlotMultiWind), `gen_phase_list` (M8 F2 T2), `find_wind_phase_color` (M3 F2) | class: `Winding` (wind matrix), `LamSlotWind` (conductor function); utility: phase list and colors | done (2026-11-21): `Winding`: static `reverse_wind_mat`, `reverse_layer`, `change_layer`, `permute_B_C`, `shift_wind_mat`, `find_wind_phase_color`, regular `get_phase_id` (connection matrix of the winding); `Conductor`: static `comp_cond_function`; `gen_phase_list` stays a utility |
| 3 | Optimization | `check_cstr`, `evaluate`, `tournamentDCD`, `update` (M2 each: OptiGenAlgNsga2Deap, OptiBayesAlgSmoot) | class: `OptiSolver` (shared base) or `OptiGenAlg` | done (2026-11-21): methods of `OptiGenAlgNsga2Deap` (`evaluate`, `check_cstr`; `tournamentDCD`, `update` static) |
| 4 | Simulation | `VarSimu.get_elec_datakeeper_dict` (M3), `VarSimu.log_datakeeper_step_result` (M1 F1) | class: `VarSimu` (as `run_multisim_step`) | done (2026-11-21): static methods of `VarSimu` |
| 5 | MeshSolution | `build_solution_data`, `build_solution_vector` (M3-4: MagFEMM, OutMag, OutLoss), `get_frame_meshsolution` (M12: loss models) | class: `SolutionData` / `SolutionVector` constructors (classmethods), `MeshSolution` method | done (2026-11-21): static `SolutionData.build_solution_data`, `SolutionVector.build_solution_vector`; `Output.get_frame_meshsolution` (it reads `output.mag`); deleted `build_meshsolution` kept as a deprecated alias of the `MeshSolution` constructor |
| 6 | Structural | `conversions` (M4: MeshSolution, Mode, SolutionVector; pol2cart, cart2pol...) | utility (math), merge with Geometry utilities | decided (2026-11-21): deprecate, the SciDataTool conversions replace it; open: not a plain duplicate (below) |
| 7 | Geometry | `inter_line_circle` (M17), `inter_line_line` (M12), `inter_circle_circle` (M2), `circle_from_3_points` (M2), `comp_flower_arc` (M4), `cut_lines_between_angle` (M2), `comp_surface_num` (M1), `merge_notch_list` (M2 G1: Lamination), `transform_hole_surf` (M6: Hole, Lamination...) | utility (geometry); class: `Lamination.merge_notch_list`, `Hole` / `Lamination` for `transform_hole_surf` | |
| 8 | Electrical | `dqh_transformation` (M8 F1 T2), `dqh_transformation_freq` (M2 F1 T1), `comp_loss_joule` (M2: LUTdq, LossModelWinding) | utility (dqh); class or merge for `comp_loss_joule` | done (2026-11-21): dqh (methods `DataTime.n2dqh`, `DataFreq.n2dqh`, `DataDual.n2dqh`, the other functions merged in `SciDataTool.dqh_transformation`, checks dropped); `comp_loss_joule` deprecated (not used); `comp_MTPA` method of `LUTdq` |
| 9 | Plot | `init_fig` (M32 G4), `get_color_legend_from_surface` (M7: laminations), `set_plot_gui_icon` (M1 G15), `Pyvista.configure_plot` (M5), `Pyvista.plot_mesh_field` (M2), `Pyvista.plot_glyph_pv` (M1), `Pyvista.plot_surf_deflection` (M1) | utility (plot); pyvista helpers merged in one module | decided (2026-11-21): pyvista plots reworked in a new object `pv_plotter_pyleecan`; `animate_as_gif` to `Data` (static); `get_color_legend_from_surface` to `Machine` (open, below) |
| 10 | FEMM | 18 used modules (draw, materials, circuits, boundary conditions, sliding band, mesh parameters; mostly F callers inside FEMM, M: MagFEMM, Surface, HoleM61) | utility package (`femm/`), with `MagFEMM` / `Surface` methods for `comp_FEMM_torque`, `comp_FEMM_Phi_wind`, `get_FEMM_BC_propname`, `get_mesh_param` | decided (2026-11-21): object dedicated to the FEMM interface, `femm_pyleecan`, in a new sub-package `femm`, all the functions as its methods; the current handler (`_FEMMHandler`) becomes `femm_pyleecan.handler` |
| 11 | GMSH | 7 modules (`draw_GMSH` M2: MagElmer, StructElmer; `gen_3D_mesh` G1 T2; the others F) | utility package (`gmsh/`) | decided (2026-11-21): object dedicated to the gmsh interface, `gmsh_pyleecan`, in a new sub-package `gmsh`, all the functions as its methods |
| 12 | Load / Save | `load` (M3 G7 C281 T113), `save` (C281), `load_switch` (generated), `Load.*` (6), `Save.*` (4) | utility package (`io/`), `load_switch` replaced by the class lookup | decided (2026-11-21): `retrocompatibility` to `classes_common` for now; Phase 2: one class to load (retrocompatibility included) and one class to save the pyleecan objects |
| 13 | Root helpers | `labels` (M117 F20), `init_environment` (G2), `path_tools` (M4 G2), `make_ndarray_equal` (M1), `get_path_binary` (M3), `GUI.log_error` (M3 G16) | utility; `log_error` with the GUI (Step 10) | |
| 14 | Other steps | `get_logger` (Step 9), `check_parent` (Step 16), `Load.import_class` (`classes_common.class_lookup`, Step 12 loaders), `Converter.Utils.ConvertionError` (shared errors, done) | other step | |

### retrocompatibility (2026-11-21)

- `classes_common/retrocompatibility.py`, written by the functions
  generator from the adapted Functions_new module (relative imports from
  `classes_common`): the conversions building objects (`OPMatrix`,
  `OPdq`, `WindingUD`) get the class from the lookup of the backend,
  `convert_init_dict(init_dict, import_class)`, kept for the conversion
  in a context variable (the converters keep their signatures; an error
  names the missing lookup).
- `Functions_new` / `Functions_pydantic` `Load/retrocompatibility.py`:
  the shared functions re-exported, `convert_init_dict(init_dict)` bound
  to the `import_class` of the backend (`load` and the tests unchanged).
- Phase 2 (PLAN.md): one class to load (retrocompatibility included) and
  one class to save the pyleecan objects.
- Checks: retrocompatibility tests as before with each backend (2
  failures before the change: parent type of `VarParamSweep`,
  `OptiConstraint._keeper_str`); class and cross tests as before; the
  `OPMatrix` conversion builds the class of each backend.

### comp_MTPA (2026-11-21)

- Method of `LUTdq` (no caller): the LUT is its second parameter
  (`MovedFunction.self_parameter`: moved first and renamed self; the
  alias keeps the legacy signature `comp_MTPA(machine, LUT, ...)`). Its
  class imports (`EEC_PMSM`, `Electrical`, `InputCurrent`, `OPdq`,
  `Simu1`) stay in the method (`local_imports`).
- Group 8 done: dqh, `comp_loss_joule` (deprecated), `comp_MTPA`.

### animate_as_gif (2026-11-21)

- Static method of `Data` (no caller). Its `VectorField` import goes in
  the method (`MovedFunction.local_imports`, comment marking the circular
  import: `VectorField` imports `DataND`, which imports `Data`).

### dqh transformations (2026-11-21)

- `n2dqh_DataTime` -> `DataTime.n2dqh`, `n2dqh_DataFreq` -> `DataFreq.n2dqh`,
  `dqh2n_DataTime` -> `DataTime.dqh2n`, `dqh2n_DataFreq` -> `DataFreq.dqh2n`
  (`MovedFunction.function`: legacy name of a renamed method); in a
  method, a function of the merged module with the name of the method is
  imported as `<name>_fct` (`n2dqh as n2dqh_fct`, `n2dqh_freq as
  n2dqh_fct`);
  `DataDual.n2dqh` (new method, `NEW_METHODS`) builds the `DataTime` of
  its time data (`axes_dt`, `values_dt`) and calls `DataTime.n2dqh`: the
  legacy checks switched the axes and values of the object to the time
  ones.
- The other functions of `Electrical.dqh_transformation` and
  `Electrical.dqh_transformation_freq` in one module,
  `Functions_new/SciDataTool/dqh_transformation.py` (`MERGED_MODULES`):
  the frequency versions renamed `n2dqh_freq`, `abc2dqh_freq`,
  `dqh2n_freq`, `dqh2abc_freq`, `get_phase_dir_freq` (same names as the
  time ones); `_check_data`, `_check_DataTime`, `_check_DataFreq` and
  their calls dropped (an `else` left empty is removed). The class
  imports of the merged module are in its functions (the classes import
  it for their methods: import cycle otherwise).
- The legacy paths are deprecated aliases (a renamed method is called on
  its class: `DataFreq.n2dqh(obj, ...)`, the legacy function accepted a
  `DataTime`); the callers of `Methods_new` / `Functions_new` call the
  methods or import from the merged module (`as` for the renamed
  functions).
- Behaviour change: a plain `DataND` (neither `DataTime`, `DataFreq` nor
  `DataDual`) has no `n2dqh` (the legacy checks accepted it); the callers
  of pyleecan pass `DataTime` / `DataFreq` objects.
- Checks: class tests, cross tests as before; dqh tests 10 passed with
  each backend (through the deprecated aliases); the three methods,
  `dqh2n_DataTime` and the aliases checked against legacy with a script;
  `Tests/New/Methods/Simulation` and `Machine` as before; `ty`:
  scidatatool 32 -> 27, electrical 143 -> 137.

### Deprecated modules (2026-11-21)

- `Plot.plot_2D_Data`, `Plot.plot_3D_Data` (no caller, replaced by the
  `Data` methods): `DEPRECATED_MODULES`, the functions generator adds a
  `DeprecationWarning` at the start of their public functions
  (`deprecate_source`, with a unit test).
- `Electrical.comp_loss_joule`: to `LamSlotWind` if used (decision); it
  is imported by `LUTdq.interp_Ploss_dqh` and `LossModelWinding.comp_loss`
  but never called: deprecated instead (the unused imports stay in the
  method modules, importing does not warn).
- [ ] `Plot.get_color_legend_from_surface` to `Machine` (decided): the
      module sets default colors in `config_dict` at import
      (`WEDGE_COLOR`, `KEY_COLOR`, read by `Slot.plot_active` and the
      `SlotM10` / `SlotM11` schematics) and the plots import its
      constants (`PHASE_COLORS`, `PLUS_HATCH`, `MINUS_HATCH`): the
      defaults and the constants to move first (with the pyvista /
      plot rework, group 9).
- [ ] `GUI.log_error` (decided: in a GUI module, where it is used most):
      16 GUI modules and 3 mesh export methods (`MeshVTK.save_vtk`,
      `MeshMat.save_vtk`, `MeshSolution.export_to_mat`) call it; moved
      with the GUI in Step 10 (`GUI_new`), the mesh methods logging
      through their logger (Step 9).
- [ ] `Structural.conversions` (decided: deprecated, replaced by
      `SciDataTool.conversions`): not a plain duplicate. `xyz_to_rphiz`,
      `rphiz_to_xyz` and the `_field` versions differ slightly (third
      component handling); `cart2pol(values, points)` /
      `pol2cart(values, points)` compute the angle from the points
      (SciDataTool: `cart2pol(field_x, field_y, phi)`); `DimError` is
      imported by `MeshSolution.get_field`. The 4 callers
      (`MeshSolution.get_field`, `SolutionVector.get_field`,
      `Mode.get_shape_pol`, `Mode.get_shape_xyz`) need equivalent calls
      checked on the numbers before the module warns.

### Group 5 (2026-11-21)

- `get_frame_meshsolution(output, group, loss_name)` takes the output:
  regular method of `Output` (`output.get_frame_meshsolution(group, ...)`
  in the 12 loss models), not of `MeshSolution`.
- `build_meshsolution` (deleted by #751, it only called the `MeshSolution`
  constructor): deprecated alias written by the functions generator
  (`REMOVED_FUNCTION_ALIASES`, for the modules deleted from legacy).
- Checks: class tests and cross tests as before; `Tests/New/Methods/Mesh`
  and `test_loss_models` as before (`test_plot_contour_1group`: pyvista
  generator bug); constructors, `get_frame_meshsolution` and the alias
  checked against legacy with a script.

### Group 2 (2026-11-21)

- Decision: `comp_cond_function` (single conductor winding function) to
  `Conductor`; the other functions to `Winding`, including the other
  public functions of their modules (`reverse_layer`, `change_layer`,
  `permute_B_C` of `reverse_wind_mat.py`, `get_phase_id` of
  `find_wind_phase_color.py`, used by `MagElmer` and the FEMM
  functions); `gen_phase_list` stays a utility.
- Static or regular (decision 2026-11-21): `self.wind_mat` is the raw
  matrix; `get_connection_mat` applies the transformations to a copy.
  The five transformations stay static (steps on an intermediate matrix
  of `get_connection_mat` / `WindingUD.init_as_*`). `get_phase_id` is a
  regular method reading the connection matrix:
  `get_phase_id(self, Nrad, Ntan, Zs, wind_mat=None)`, default
  `self.get_connection_mat()`, legacy body in the static
  `_get_phase_id(wind_mat, ...)`; the callers holding `wind_mat =
  obj.get_connection_mat(...)` call `obj.get_phase_id(...,
  wind_mat=wind_mat)` (MagElmer, FEMM). `find_wind_phase_color` stays
  static: the plots call it without matrix on purpose (no winding,
  `WindingSC`, `get_connection_mat` error: first phase color); it calls
  `Winding._get_phase_id`. Regular method with the guard in the plots:
  Step 16.
- Generator support added (`moved_functions.py`): several moved functions
  in one legacy module (tuple in `MOVED_FUNCTIONS`: one method module
  each, one deprecated alias each, calls between them on the class); a
  static method called outside its class (`LamSlotWind.plot`,
  `comp_wind_function`, `MagElmer.solve_FEA`) goes through the class,
  imported in the calling function; the same redirection in the
  functions generator (`Functions_new` FEMM functions call the method,
  not the deprecated alias); bound functions (`MovedFunction.bound`:
  regular method with the parameter optional, static `_<method>`
  implementation, receiver taken from the nearest `x = obj.getter(...)`
  assignment of the caller). Class generator: a module constant of a
  static method is read on the class (`Winding.PHASE_COLORS`; it was
  read on the first argument); the imports of the module's own class in
  the functions and `if TYPE_CHECKING:` blocks are removed
  (`Winding`, `XOutput`, `DataFreq`, `DataND`, `VectorField`, `VarSimu`).
  Type hints: `find_wind_phase_color` takes `wind_mat` or None and
  returns `(color, sign)` (overrides; `ty` machine stays at 38).
- Checks: `Tests/Classes` 3937 passed; `Tests/New/Classes` 2855 passed and
  `test_copy_out` failed with each backend; `Tests/New/Cross` 1405 passed;
  `Tests/New/Methods/Machine` 77 passed, 2 failed as before
  (`test_get_polar_eq_SCIM`, `test_notch`: `Circle(xy=...)`); winding
  tests and plots (29 files): the same 23 failures as before the change;
  the 8 moved functions (and `get_phase_id` with its default) and the
  aliases checked against legacy with a script, on each backend.

### Groups 3 and 4 (2026-11-21)

- Optimization: only `OptiGenAlgNsga2Deap.solve` calls the four functions
  (`OptiBayesAlgSmoot.solve` imported them without using them, and has its
  own `evaluate(input_x)`): methods of `OptiGenAlgNsga2Deap`, not of
  `OptiSolver` (an `evaluate` on the base would be overridden with another
  signature). The functions work on the DEAP individuals of
  `create_toolbox`. `choseDCD` (helper of `tournamentDCD`) becomes a static
  method too.
- Simulation: `get_elec_datakeeper_dict` and `log_datakeeper_step_result`
  static methods of `VarSimu` (they do not use the object).
- Generator support added: a static method called from a daughter class
  (`VarLoadCurrent`, `VarLoadVoltage`: `self.get_elec_datakeeper_dict()`),
  or from a static method (`run_multisim_step`:
  `VarSimu.log_datakeeper_step_result`, class imported in the function);
  the helpers of a static method module are called on the class (class
  generator; `self.choseDCD` before, a NameError); the Python 2 branches of
  the `sys.version_info` tests are removed (`remove_python2_branches`, both
  pipelines: `evaluate` was kept as a broken import of the legacy path,
  the class generator does not inline a top-level `if`).
- Checks: `Tests/Classes` 3937 passed; `Tests/New/Classes` 2855 passed and
  `test_copy_out` failed with each backend; `Tests/New/Cross` 1405 passed;
  legacy `test_zdt3`, `test_Binh_and_Korn` pass. In `Tests/New`, these two
  and `test_post_var_simu` fail before reaching the moved methods, as
  before this change (custom setters: `OptiDesignVarInterval._setter_str`,
  DataKeeper functions given as strings, Step 13); `tournamentDCD`,
  `get_elec_datakeeper_dict` and the deprecated aliases checked against
  legacy with a script (same selection with a fixed seed).
- `ty`: optimization 65 -> 64, simulation 73 -> 84 (the moved functions
  are checked in `Methods_new` now: DataKeeper functions given as
  strings).
- Found on the way (#751, fixed): `LossModelBertotti.plot_fitting` and
  `LossModelSteinmetz.plot_fitting` imported the `comp_loss_val` helper of
  the `comp_coeff` method module (a module function decorated
  `@staticmethod` in legacy): runtime import of a method source in the
  classes (`test_no_runtime_import_of_method_sources` failed since the
  #751 merge). Class generator: a `@staticmethod` module function is a
  helper like an undecorated one, and a helper imported from another
  method module of the class is called on the class
  (`_remove_sibling_helper_imports`): `comp_loss_val` is a static method
  in the body of both classes, called by `comp_coeff` and `plot_fitting`
  as `self.comp_loss_val`.

## Step 9: logger chain

`get_logger` walks the parents to find a `logger_name`. Calls on 2026-11-17:
169 in 94 `Methods_new` modules, 6 in `Functions_new`
(`Functions_new/get_logger.py`, `PyleecanClass.get_logger`).

- [ ] Inventory of the `logger_name` values and where they are set
      (`Simulation`, `Output`, `XOutput`, optimization), and of the log files
      written per simulation.
- [ ] Choose the target: per-module loggers (`logging.getLogger(__name__)`),
      or a context logger (a `contextvars` value set by `Simulation.run` and
      read by a module-level helper). The per-simulation log file and the
      multi-simulation logs must keep working.
- [ ] Generator pass in the shared pipeline rewriting `self.get_logger()` /
      `get_logger(obj)`, with unit tests; same pass in the functions generator.
- [ ] Remove `get_logger` (function and base method), or keep it as a
      deprecated alias.

## Step 10: GUI, first pass

Inventory of the legacy GUI (`src/pyleecan/GUI`, 2026-11-21):

| Item | Count |
|---|---|
| Python modules | 375, of which 92 Qt Designer modules (`Ui_*`) |
| Modules importing classes | 89 (104 distinct classes) |
| `Gen_*` widget classes (legacy GUI generator, from the CSV files) | 64 |
| `check()` calls (validation of the edited objects) | 74 in 55 modules |
| `except SlotCheckError` | 53 |
| Direct object parent reads (`hole.parent.parent`, `lam = self.hole.parent.copy()`) | 9 in 5 modules |
| Field assignments from widgets (`self.obj.X = ...`, `self.lam...`, `self.slot...`) | about 94 |
| `-1` conventions | 12 |
| `get_logger` calls | 14 |
| Legacy tests (`Tests/GUI`), generated copies (`Tests/New/GUI`) | 78, 78 |

Most of the parent dependency is indirect: the dialogs edit a slot, hole or
winding inside its lamination and call its methods (`check()`, `comp_*`),
which read the parents. Step 11 changes these signatures: the GUI must be
generated first so that the same passes rewrite its calls.

- [ ] GUI generator (`generate_gui_new.py`, new generator module): `GUI_new`
      from `GUI` with the shared pipeline (`modernize.py`: imports of
      `Classes_new` / `Functions_new` and of the sub-packages, keyword
      constructors, shared errors from `classes_common/errors.py`, `-1`
      conventions); `Ui_*` modules and resources copied; `GUI_pydantic` by
      import rewriting (same as `generate_function_pydantic.py`). Unit tests
      per pass.
- [ ] `Gen_*` classes generated from `ClassInfo` (min, max, unit,
      description) instead of the CSV files (`Generator/gui_generator.py`),
      so that they survive the Phase 2 removal of the CSV files.
- [ ] Validation errors: the GUI catches the shared errors whatever the
      backend. On assignment, the dataclass backend raises
      `CheckTypeError`/`CheckMinError`/`CheckMaxError`, pydantic raises
      `ValidationError`: one base (or a conversion in `LegacyModel`) decided
      with the contract tests; the error message shown on the field.
- [ ] `Tests/New/GUI` generated against `GUI_new` / `GUI_pydantic` (backend
      alias like `backend_classes`); they import the legacy GUI today.
- [ ] The GUI calls of the logger chain (Step 9) and of the moved functions
      (Step 6, Step 8) rewritten by the same passes.
- [x] Decided (2026-11-21): both `GUI_new` (dataclass + dacite) and
      `GUI_pydantic` are kept, for the final backend comparison (Step 18:
      the same GUI scenarios run on each backend).

## Step 11: parent links, first pass

Parent reads found in the legacy methods on 2026-11-15:

| Package | Parent reads | Classes | Typical use |
|---|---|---|---|
| Geometry | 0 | 12 | none |
| Slot | 261 | 56 | slot or hole reads its lamination (`Rint`, `Rext`, `get_Rbo()`, `is_stator`, `get_label()`) |
| Machine | 142 | 19 | winding, conductor and end winding read the slotted lamination; bore and notch read the lamination |
| Simulation | 118 | 25 | a model reads the simulation, then the output (`self.parent.parent`) |
| Loss | 38 | 9 | loss models walk up to the machine or output |
| Output | 25 | 5 | sub-outputs read the `Output` |
| Optimization | 4 | 2 | |
| Functions | 3 files | | `check_parent`, `assign_femm_surface`, `get_logger` |

These reads follow five patterns:

1. A child reads its container's data: pass the container as an argument, or move
   the method onto the container.
2. A simulation model walks up to the simulation and output: pass the context
   explicitly (`run(output)`).
3. Labels (`self.parent.get_label()`): the caller passes the label.
4. Navigation helpers (`get_machine_from_parent`, `check_parent`): explicit arguments.
5. The logger chain: Step 9.

- [ ] Script classifying every `self.parent` read of `Methods_new` by pattern,
      and by "mechanical" (the container is known from the call sites in
      `Methods_new`) or not; report here.
Signature rule (decided 2026-11-17): the container becomes an **optional
argument with a parent fallback**, and the container is passed, not the
values read from it:

```python
def comp_height(self, lam: "Lamination | None" = None) -> float:
    lam = container_or_parent(self, lam, "lam")   # fallback: self.parent
    Rbo = lam.get_Rbo()
```

- Phase 1: the fallback is silent. Old calls (`slot.comp_height()`) keep
  working, so the legacy-derived tests and user scripts run unchanged and the
  parity stays measurable; the generator makes the new code (`Methods_new`,
  `Functions_new`) pass the container explicitly.
- Phase 2: the fallback raises a `DeprecationWarning` (the parent feature is
  going away); a later release removes the fallback and the parent links,
  and the argument becomes required.
- Every fallback goes through one shared helper (`container_or_parent`, in
  `classes_common`), so the Phase 2 warning is added in one place and every
  site is found by a search. Each site is also listed in
  [Phase 2 deprecations](#phase-2-deprecations).
- Step 16 may still narrow a method to plain values where it clearly helps.

- [ ] Shared helper `container_or_parent` (both backends), with unit tests.
- [ ] Generator passes, one pattern per increment (method, function and test
      generators), with unit tests and the parity tests unchanged; each pass
      reports the methods given a fallback argument (generated list, copied
      to [Phase 2 deprecations](#phase-2-deprecations)).
- [ ] Report the reads left for Step 16.

## Step 12: freeze

- [ ] Move the "loaders" and "static_imports" passes (with dynamic imports and
      normalization renames, the chain that depends on the class imports)
      from the class generator to the method generator, or make them produce
      the final code in `Methods_new`: 31 modules still call
      `import_class("pyleecan.Classes", "X")`, so `ty` sees the legacy types
      there and a frozen copy would keep them.
- [ ] Remove the compatibility shim of the class generator
      (`_read_method_source`: `to_legacy_names`).
- [ ] No legacy object built in `Methods_new`: `SlotUD2._set_split_active_surf_dict`
      and `VarLoad._set_OP_matrix` import the legacy
      `Functions.Load.import_class` and build `pyleecan.Classes` objects with
      `init_dict=`; `VarLoad` imports the legacy `Functions.load.load_init_dict`.
- [ ] Parity baseline: run `Tests/New/Methods` per package with each backend;
      record the results here (passed / failed per package); compare the
      method results between backends (Step 4 item).
- [ ] Freeze mechanism (decided 2026-11-17: all at once, since Steps 13–17
      cover every package): `GUI_new` frozen with them; all sub-packages in `FROZEN_PACKAGES`
      (`generate_methods_new.py`); a list of the hand-written modules in the
      functions generator (`generate_function_new_classes.py`), which keeps
      writing the others and the deprecated aliases.
- [ ] Full regeneration: generated classes unchanged by the freeze.
- [ ] CLAUDE.md: `Methods_new` and the frozen `Functions_new` modules edited by
      hand; which generator modules are still in use.

## Step 13: custom property setters and getters

Legacy classes with their own property setter or getter methods, inlined in
the new classes but not wired to the fields (a dataclass or pydantic field has
no property). The `slot` ones (`SlotW11`/`SlotW11_2`/`SlotW23._set_W3`,
`SlotUD2._set_split_active_surf_dict`) are wired by the legacy layers
(`WIRED_SETTER_SUBPACKAGES`, `classes_common/custom_setters.py`).

- [ ] `ParamExplorer._set_getter` / `_set_setter` (e.g. `setter="simu.input"`;
      `Tests/New/Classes/test_copy.py::test_copy_out` fails): two storages
      (`_setter_str` / `_setter_func`) and custom getters.
- [ ] `DataKeeper._set_keeper`: same pattern (str, lambda or path to a callable).
- [ ] `VarLoad._set_OP_matrix`.
- [ ] `DataND._set_values` / `_get_field` / `_get_freqs`, `Data._set_normalizations`.
- [ ] `RuleComplex._set_fct_name`.

For each: an explicit conversion (field validator, or a method building the
value), the same in both backends.

## Step 14: type hints, second pass

Conventions: class annotations use imports under `if TYPE_CHECKING:` (lazy
annotations of Python 3.14, no `from __future__ import annotations`, which the
class generator does not inline); no runtime import, so no cycle and the
backend import rewriting keeps working.

Coverage of the first pass (parameters / returns hinted, `ty` diagnostics;
simulation, loss, output and magnetics after the #751 merge):

| Package | Parameters | Returns | ty |
|---|---|---|---|
| geometry | 135/164 | 125/131 | 21 |
| slot | 832/886 | 657/694 | 20 |
| material | 19/19 | 12/12 | 2 |
| machine | 445/458 | 321/337 | 38 |
| simulation | 92/104 | 83/92 | 73 |
| loss | 45/45 | 35/35 | 64 |
| output | 101/124 | 59/82 | 83 |
| optimization | 16/41 | 8/17 | 65 |
| converter | 77/95 | 86/100 | 26 |
| electrical | 35/46 | 41/46 | 143 |
| magnetics | 58/70 | 16/18 | 159 |
| force | 11/21 | 5/9 | 68 |
| structural | 9/23 | 12/16 | 19 |
| mesh | 205/248 | 87/113 | 44 |
| post | 2/3 | 2/3 | 5 |
| elmer | 1/11 | 7/17 | 5 |
| import_data | 12/14 | 17/19 | 5 |
| gui_option | 4/4 | 6/6 | 0 |
| scidatatool | 318/398 | 26/78 | 32 |

Recurring causes, to solve once where possible:

- [ ] Methods of the daughters not declared on the base class (abstract
      methods to add): `Line` (`split_line`, `get_begin`, `get_end`,
      `get_center`, `is_arc`, `is_on_line`, `comp_radius`, about 18
      diagnostics), `Machine` (`rotor`, `stator`), `Data`
      (`get_periodicity`, `get_axis_periodic`, `is_components`,
      `get_length`), `Solution` (`field`).
- [ ] Optional fields used without check: add the check (explicit error), or
      type the field as not optional (see "Nullable fields" in PLAN.md).
- [ ] Implicit `None` returns (a missing case: raise an error or return a value).

Review list by package (behaviour or class definition to decide):

- Geometry:
  - [ ] `get_patches` uses `"--" in linestyle` with a None default (PolarArc,
        SurfLine, Trapeze: `replace`/`in` on an optional style);
  - [ ] `Segment.intersect_line` can return None; a `Polygon` returned for
        `list[Polygon]`; one implicit `None` return.
- Slot:
  - [ ] implicit `None` returns: `SlotW14`/`SlotW15`/`SlotW29.comp_surface_opening`,
        `SlotW14`/`SlotW29.comp_surface_wedge` (`wedge_type` other than 0 and 1),
        `SlotW23.get_H1` (second `if self.H1_is_rad` always true),
        `HoleUD.comp_surface_magnet_id` (unknown label), `HoleM52R.plot_schematics`;
  - [ ] `Hole.plot`: `mag_surf` stays `None` when no magnet surface matches its
        label (an `AttributeError` follows): raise an explicit error;
  - [ ] `HoleM52R.plot_schematics`: `ax.get_legend()` may be `None`.
- Material:
  - [ ] `ModelBH.fit_model` (after the Step 5 fix).
- Machine:
  - [ ] `Winding.export_to_csv`, `WindingUD.import_from_csv`: `file_path=None`
        but used as a str (required parameter?);
  - [ ] `LamHole`/`LamHoleNS._plot_arrow_mag`: the magnet surface stays `None`
        when no label matches, `ax` may be `None`;
  - [ ] `LamSlotMag.get_all_mag_obj`: optional `mat_type`/`mag` fields assigned
        without check;
  - [ ] implicit `None` returns: `Frame.plot`, `LamSquirrelCage.plot_schematics_scr`,
        `LamSlotMag.get_magnet_by_label`;
  - [ ] `LamSlotWind.comp_mmf_unit`: lists given to ndarray fields of `Data1D`;
        `LamSlotWind.plot`: lists for `FancyArrowPatch` positions (tuple);
        `Machine.plot_anim_rotor`: `Patch.xy`.
- Simulation:
  - [ ] `ParamExplorer` (`getter`, `setter`), `DataKeeper` (`keeper`): str
        given to callable fields (Step 13);
  - [ ] `VarParamSweep.generate_simulation_list`: `init_dict=` constructor
        argument (legacy layer only);
  - [ ] optional fields used without check: `VarSimu.set_reused_data`
        (`simu.mag`, `simu.elec`, `output.mag.internal`),
        `generate_simulation_list` (`ref_simu.copy`), `Input.comp_axis_*`
        (`int | None` compared);
  - [ ] `InputCurrent.gen_input`: lists given to ndarray fields;
        `get_ref_simu_index`: `int | None` returned.
- Loss:
  - [ ] optional fields used without check: `LossModelBertotti` /
        `LossModelSteinmetz.comp_coeff` (`mat_type.mag.LossData.get_data`),
        `Loss.comp_axes` (`output.mag.meshsolution`), `Loss.comp_all_losses`;
  - [ ] private matplotlib `Axes._get_lines` (`comp_coeff` plots);
  - [ ] `LossFEA.run`: ty narrows `self.model_dict` to the type of the dict
        literal assigned, then rejects `LossModelMagnet` (ty quirk, field typed
        `dict[str, LossModel]`).
- Output:
  - [ ] `OutLossModel.__add__`/`__radd__`/`__sub__`/`__rsub__`: `other` is also
        `0` (`sum()` start value), not documented;
  - [ ] `OutElec.get_electrical`: str keys checked as indices;
  - [ ] `OutMag.store`, `OutForce.store`, getters: optional fields used without
        check; `plot_B_mesh`: decorated `plot_mesh_field` (ty: missing `self`).
- Optimization:
  - [ ] `OptiGenAlgNsga2Deap` / `OptiBayesAlgSmoot` (`solve`, `plot_pareto`,
        `create_toolbox`): untyped DEAP/SMT objects, optional fields,
        `init_dict=` constructor argument.
- Converter:
  - [ ] `convert_hole_to_P`: optional `hole` list and `other_dict` entries used
        without check; `convert_slot_to_P`: `init_dict=` constructor argument,
        `wedge_mat` assigned on an optional slot;
  - [ ] `add_rule_winding`: dict with bool keys given to `dict[str, Any]`.
- Electrical:
  - [ ] `Electrical.gen_drive`: input built with `type(output.simu.input)(...)`
        (ty false positive).
- [ ] Other packages (electrical, magnetics, force, structural, mesh,
      scidatatool...): review their diagnostics, mostly the recurring causes.

Then:

- [ ] `py.typed` marker; checker made stricter step by step.

## Step 15: utility functions

First audit (2026-11-15, from imports): 26 of the 145 legacy `Functions`
modules are used by a single class (17 after review, Step 6), and 41 modules
are imported by no class, function or GUI module. Step 8 sorts them by
generator; this step finishes by hand what the generator could not do.

- [ ] Finish the module targets of Step 8 that need hand changes.
- [ ] Complete the type hints of the utility functions (from the Step 8 draft).
- [ ] Mark the class-independent functions for `src/pyleecan/utils/` (Phase 2).

## Step 16: parent links, second pass

Same signature rule as Step 11 (optional container argument, fallback through
`container_or_parent`); each new site is added to
[Phase 2 deprecations](#phase-2-deprecations).

- [ ] Remove the reads left by Step 11, package by package (Slot, Machine,
      Simulation, Loss, Output, Optimization).
- [ ] Function helpers with explicit arguments: `check_parent`,
      `assign_femm_surface`.
- [ ] Tests of a refactored package hand-maintained; numerical parity against
      legacy, from the Step 12 baseline.
- [ ] No parent read left in `Methods_new` and `Functions_new` outside
      `container_or_parent`; the parent links stay only in the legacy layer.
- [ ] The `GUI_new` calls of each refactored package updated in the same
      increment.
- [ ] `Winding.find_wind_phase_color` as a regular method reading the
      connection matrix (like `get_phase_id`): `LamSlotWind.plot` and
      `LamSlotMultiWind.plot` call it on the winding when there is one,
      and keep the first phase color without winding / for `WindingSC`
      (Step 8 group 2).

## Step 17: GUI, second pass

- [ ] Direct parent reads of the dialogs (9 in 5 modules: hole and magnet
      pages reading `hole.parent.parent`, lamination copies): the container
      passed explicitly to the page.
- [ ] Parent wiring the dialogs rely on (an object edited inside its
      container so that its methods see the lamination): replaced by the
      explicit container of Step 16.
- [ ] Input validation on the target model: the dialog edits a working copy,
      validation by the model (validated assignment or `model_validate` of the
      edited dump), errors reported per field; widget limits from `ClassInfo`
      only; the `check()` errors kept for the geometric consistency.
- [ ] GUI tests hand-maintained, with each backend; machines built with the
      GUI give the same dump as with the legacy GUI.
- [ ] The `-1` / `None` conventions left in the GUI removed with the legacy
      layer (Phase 2).

## Step 18: backend comparison (benchmark)

Same scenarios on each backend (`--backend=dataclass|pydantic`, `GUI_new` /
`GUI_pydantic`), with the legacy classes as a reference where they apply.
First figures: creation time in Step 2 of the plan (`Segment`, `LamSlotWind`).

- [ ] Micro benchmarks: creation, validated assignment (valid and invalid
      values), `model_dump` / `model_validate`, `model_copy`, `==`, import
      time of the class packages.
- [ ] Machine files: load and save of the 37 files of `Data/Machine`, memory.
- [ ] Methods and simulations: the parity baseline of the freeze (Step 12)
      timed per package; a few full simulations (FEMM excluded or timed
      apart).
- [ ] GUI scenarios: open a machine, edit the fields of a lamination and a
      slot (validation errors included), save; same scripted scenario with
      each GUI (Qt test driver).
- [ ] Report in the backlog (time, memory, behaviour differences found) and
      decision for Phase 2.

## Phase 2 deprecations

Register of what Phase 1 keeps for compatibility and Phase 2 must deprecate
or remove. Every Phase 1 step adding such a compatibility path adds its sites
here.

Parent fallbacks (Steps 11 and 16): in Phase 2, `container_or_parent` raises a
`DeprecationWarning` when the container is not given; a later release removes
the fallback, the parent links, and makes the argument required.

| Method | Container argument | Added in |
|---|---|---|
| (filled by the Step 11 passes) | | |

Note: the parent links then outlive the legacy layer for one or more
releases: Phase 2 must keep them (or a minimal version) as a deprecated
feature when it deletes `LegacyClass` / `LegacyModel`.

Deprecated function aliases (already warn in Phase 1, removed in Phase 2):

| Old path | New location | Added in |
|---|---|---|
| `Functions.MeshSolution.get_area` | `MeshSolution.get_area` | Step 6 |
| `Functions.MeshSolution.get_indices_limited` | `MeshSolution.get_indices_limited` | Step 6 |
| `Functions.Simulation.VarSimu.run_multisim_step` | `VarSimu.run_multisim_step` | Step 6 |
| (Step 8 moves, `get_logger` of Step 9) | | |

- [ ] Decide which other legacy behaviours removed with the legacy layer need
      a deprecation period (`-1` default, `None` everywhere, `as_dict` /
      `from_dict` / `copy` / `compare`, `init_dict=` / `init_str=`, legacy
      class names when loading files) and add them here.

## Infrastructure

- [ ] CI running the suite once per backend (no CI configuration in the
      repository yet): `pytest Tests/New/Classes --backend=dataclass` and
      `--backend=pydantic`, plus `Tests/Classes`.

## Phase 2

- [ ] Check the imports (time and side effects) of the common use cases: main
      simulations, the machine GUI, the main plots. Today
      `import pyleecan.definitions` loads matplotlib and the user configuration
      (`get_config_dict`). (The config file is already written only when its
      content changes, atomically: done in Phase 1.)
- [ ] Executable: uv does not build executables, but it replaces most of the
      legacy `generate_pyleecan_exe.py` (clone, virtual environment,
      requirements):
  - `uv sync --frozen`, then `uv run --with pyinstaller pyinstaller pyleecan.spec`;
  - the `.spec` is rewritten: no hardcoded `site-packages` paths (covered by
    `pyinstaller-hooks-contrib`), no `Class_Dict.json`, hidden imports updated
    to the new package names;
  - the Inno Setup script (`pyleecan.iss`) and the icon are kept; the version
    is read from `pyproject.toml`.
- [ ] Repository layout: see the table of PLAN.md.
