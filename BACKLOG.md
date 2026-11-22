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

- [x] Generator bug (pre-existing, fixed 2026-11-21 with the pyvista
      object): the pyvista import pass turns
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
- [x] (2026-11-21) every module that stays a utility gets the hints
      (not the deprecated aliases, the vendored code, nor
      `Load/retrocompatibility.py`, split into `classes_common` by text):
      65 modules; `ty` on `Functions_new` 428 -> 582 diagnostics, mostly
      optional values used without check (`ax: Axes | None` in the
      SciDataTool plots) and wrong documented return types (Step 15).
      Tests as before.
- [x] Type hints drafted for the functions that stay utilities: run the
      `type_hints.py` pass in the functions generator (same rules as the
      methods), report the coverage and the `ty` diagnostics of
      `Functions_new`.

### Converter rule functions (2026-11-21)

The 24 `Converter/MotorCAD` modules are the functions of the complex
conversion rules: `other_to_P(self, ...)` / `P_to_other(self, ...)`, with
`self` the `RuleComplex` (it reads `unit_type`, `param_dict`, `get_other`,
`set_P`), loaded by name from `RuleComplex.fct_name`.

- [x] Static registry (decided): `Functions_new/Converter/rule_functions.py`,
      generated (`function_module_names.rule_functions_source`):
      `RULE_FUNCTIONS = {legacy rule name: module}` and
      `rule_function_module(fct_name)`; the `__import__` by name of
      `_set_fct_name` replaced (`redirect_rule_module_name`, local import),
      and `RuleComplex.convert_to_P` / `convert_to_other` read the registry
      when they run (`legacy_fixes`), so the unwired custom setter is no
      longer needed. Result: `Tests/New/Methods/Converter` 49 passed on
      both backends (43 failed before: `other_to_P` missing; the pydantic
      loader had a broken module name).
- [x] `slotW23_H1` deprecated (decided: no rule uses it,
      `add_rule_slotW23` converts H1 with a simple rule); not imported by
      the registry, loaded on request (`DEPRECATED_RULE_FUNCTIONS`, it
      warns).
- [ ] `path_tools.rel_file_path` never worked (found 2026-11-21): the
      relative `importName("..definitions")` always fails silently and
      `normpath` / `abspath` are not imported, so it returns the path
      unchanged (`DMatSetup` material paths stay absolute). Kept as is
      (parity); to fix with the maintainer (it changes the saved paths).
- [x] (2026-11-22, Step 15) Docstrings of the rule functions: `self` renamed
      `rule` (`rename_rule_self`, `function_module_names.py`, run by the
      functions generator on the `Converter/MotorCAD` modules; the
      `RuleComplex` calls them positionally), docstring `rule : RuleComplex`
      (they said `ConvertMC`), so the hint pass types it: 46/46 functions.
      `ty` on `Functions_new/Converter` 69 -> 71: the typed `rule` shows
      `other_unit_dict=None` given to `Rule.get_other` (`winding_layer`).
      Converter tests 49 passed with each backend. Test:
      `Tests/New/test_rename_rule_self.py`.

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
| 1 | Dead code | `Plot.plot_2D_Data`, `Plot.plot_3D_Data` (already deprecated), `Plot.animate_as_gif`, `Plot.Pyvista.get_arrows_plt`, `Geometry.create_surface`, `FEMM.comp_FEMM_Jcus`, `FEMM.create_FEMM_bar`, `Electrical.comp_MTPA`, `getattr_recursive`, `short_filepath`, `Converter.Utils.EquivalentError` (no caller) | remove | done (2026-11-21): deprecated (`DEPRECATED_MODULES`, the functions warn): `get_arrows_plt`, `create_surface`, `comp_FEMM_Jcus`, `create_FEMM_bar` (left out of `femm_pyleecan` / `pv_plotter_pyleecan`, at their legacy path), `getattr_recursive`, `short_filepath`; `plot_2D_Data`, `plot_3D_Data` deprecated before, `animate_as_gif` and `comp_MTPA` moved; `EquivalentError` (a class, shared error) removed in Phase 2 |
| 2 | Winding | `reverse_wind_mat`, `shift_wind_mat` (M6: Winding, WindingSC, WindingUD), `comp_cond_function` (M2: LamSlotWind, LamSlotMultiWind), `gen_phase_list` (M8 F2 T2), `find_wind_phase_color` (M3 F2) | class: `Winding` (wind matrix), `LamSlotWind` (conductor function); utility: phase list and colors | done (2026-11-21): `Winding`: static `reverse_wind_mat`, `reverse_layer`, `change_layer`, `permute_B_C`, `shift_wind_mat`, `find_wind_phase_color`, regular `get_phase_id` (connection matrix of the winding); `Conductor`: static `comp_cond_function`; `gen_phase_list` stays a utility |
| 3 | Optimization | `check_cstr`, `evaluate`, `tournamentDCD`, `update` (M2 each: OptiGenAlgNsga2Deap, OptiBayesAlgSmoot) | class: `OptiSolver` (shared base) or `OptiGenAlg` | done (2026-11-21): methods of `OptiGenAlgNsga2Deap` (`evaluate`, `check_cstr`; `tournamentDCD`, `update` static) |
| 4 | Simulation | `VarSimu.get_elec_datakeeper_dict` (M3), `VarSimu.log_datakeeper_step_result` (M1 F1) | class: `VarSimu` (as `run_multisim_step`) | done (2026-11-21): static methods of `VarSimu` |
| 5 | MeshSolution | `build_solution_data`, `build_solution_vector` (M3-4: MagFEMM, OutMag, OutLoss), `get_frame_meshsolution` (M12: loss models) | class: `SolutionData` / `SolutionVector` constructors (classmethods), `MeshSolution` method | done (2026-11-21): static `SolutionData.build_solution_data`, `SolutionVector.build_solution_vector`; `Output.get_frame_meshsolution` (it reads `output.mag`); deleted `build_meshsolution` kept as a deprecated alias of the `MeshSolution` constructor |
| 6 | Structural | `conversions` (M4: MeshSolution, Mode, SolutionVector; pol2cart, cart2pol...) | utility (math), merge with Geometry utilities | done (2026-11-21): deprecated, its functions in `SciDataTool.conversions` (below) |
| 7 | Geometry | `inter_line_circle` (M17), `inter_line_line` (M12), `inter_circle_circle` (M2), `circle_from_3_points` (M2), `comp_flower_arc` (M4), `cut_lines_between_angle` (M2), `comp_surface_num` (M1), `merge_notch_list` (M2 G1: Lamination), `transform_hole_surf` (M6: Hole, Lamination...) | utility (geometry); class: `Lamination.merge_notch_list`, `Hole` / `Lamination` for `transform_hole_surf` | done (2026-11-21): `inter_line_circle`, `inter_line_line` (with `find_line_eq`), `inter_circle_circle`, `circle_from_3_points`, `comp_flower_arc`, `cut_lines_between_angle`, `comp_surface_num` merged in `utils/geometry.py` (`MERGED_MODULES`, the legacy paths deprecated aliases, the callers redirected); static `Lamination.merge_notch_list`, static `Hole.transform_hole_surf` (the alias of `merge_notch_list` imports the shared `NotchError`) |
| 8 | Electrical | `dqh_transformation` (M8 F1 T2), `dqh_transformation_freq` (M2 F1 T1), `comp_loss_joule` (M2: LUTdq, LossModelWinding) | utility (dqh); class or merge for `comp_loss_joule` | done (2026-11-21): dqh (methods `DataTime.n2dqh`, `DataFreq.n2dqh`, `DataDual.n2dqh`, the other functions merged in `SciDataTool.dqh_transformation`, checks dropped); `comp_loss_joule` deprecated (not used); `comp_MTPA` method of `LUTdq` |
| 9 | Plot | `init_fig` (M32 G4), `get_color_legend_from_surface` (M7: laminations), `set_plot_gui_icon` (M1 G15), `Pyvista.configure_plot` (M5), `Pyvista.plot_mesh_field` (M2), `Pyvista.plot_glyph_pv` (M1), `Pyvista.plot_surf_deflection` (M1) | utility (plot); pyvista helpers merged in one module | done (2026-11-21): pyvista functions in `pv_plotter_pyleecan` (static methods); `animate_as_gif` to `Data`; `get_color_legend_from_surface` static method of `Machine` (the colors read from the configuration when called); `init_fig` to `utils`; `set_plot_gui_icon` to the GUI (`Tools`, imported by `LamSlotWind.plot_mmf_unit` when it plots) |
| 10 | FEMM | 18 used modules (draw, materials, circuits, boundary conditions, sliding band, mesh parameters; mostly F callers inside FEMM, M: MagFEMM, Surface, HoleM61) | utility package (`femm/`), with `MagFEMM` / `Surface` methods for `comp_FEMM_torque`, `comp_FEMM_Phi_wind`, `get_FEMM_BC_propname`, `get_mesh_param` | done (2026-11-21): object dedicated to the FEMM interface, `femm_pyleecan`, in a new sub-package `femm`, all the functions as its methods; the current handler (`_FEMMHandler`) becomes `femm_pyleecan.handler` |
| 11 | GMSH | 7 modules (`draw_GMSH` M2: MagElmer, StructElmer; `gen_3D_mesh` G1 T2; the others F) | utility package (`gmsh/`) | done (2026-11-21): `gmsh_pyleecan` gathers the gmsh functions as static methods (as close as possible to legacy, to be improved later) |
| 12 | Load / Save | `load` (M3 G7 C281 T113), `save` (C281), `load_switch` (generated), `Load.*` (6), `Save.*` (4) | utility package (`io/`), `load_switch` replaced by the class lookup | decided (2026-11-21): `retrocompatibility` to `classes_common` for now; Phase 2: one class to load (retrocompatibility included) and one class to save the pyleecan objects; closed as it is (decided 2026-11-21) |
| 13 | Root helpers | `labels` (M117 F20), `init_environment` (G2), `path_tools` (M4 G2), `make_ndarray_equal` (M1), `get_path_binary` (M3), `GUI.log_error` (M3 G16) | utility; `log_error` with the GUI (Step 10) | done (2026-11-21): `labels`, `path_tools`, `init_environment`, `make_ndarray_equal`, `get_path_binary` moved to the `utils` package (`MOVED_MODULES`: whole modules, the legacy paths deprecated modules re-exporting the names); `log_error` moved to the GUI (`GUI_new/Tools/log_error.py`, the mesh methods log their errors) |
| 14 | Other steps | `get_logger` (Step 9), `check_parent` (Step 16), `Load.import_class` (`classes_common.class_lookup`, Step 12 loaders), `Converter.Utils.ConvertionError` (shared errors, done) | other step | covered by the other steps (decided 2026-11-21) |

### Type hints of the Step 8 methods (2026-11-21)

- Moved methods (`Methods_new`): 94/94 parameters, 29/29 returns, with
  overrides for the docstrings missing types (`type_hints.py`); DEAP
  individuals typed `Any`; `callable` / `function` -> `Callable`.
- Interface objects and merged module (`Functions_new`): the type hint
  pass runs in the functions generator for `HINTED_FUNCTION_MODULES`
  (after the import rewriting), and covers the methods of the classes:
  `femm_pyleecan` 133/133 parameters, 23/23 returns; `gmsh_pyleecan`
  48/48, 11/11; `pv_plotter_pyleecan` 32/32, 5/5;
  `SciDataTool.dqh_transformation` 48/48, 15/15. The handler of
  `femm_pyleecan` comes from `classes_common.femm_handler` (it was the
  legacy class).
- `ty` with the hints: femm_pyleecan 97, gmsh_pyleecan 68,
  pv_plotter_pyleecan 5, dqh_transformation 5 diagnostics (known causes:
  `Machine.rotor`, optional fields, legacy 0/1 for bool, `init_dict`);
  Methods_new optimization 64, scidatatool 41, output 107.
- Legacy bugs found: `animate_as_gif` used an undefined `data` (NameError,
  fixed in `legacy_fixes.py`); [ ] `comp_MTPA` (no caller) calls
  `EEC.comp_parameters` with arguments that no longer exist (`Trot`,
  `Id_array`, `Iq_array`) and `EEC.solve` with too many arguments: to
  update to the current EEC API.

### PyVista object (2026-11-21)

- `pv_plotter_pyleecan` (`Functions_new/Plot/Pyvista/pv_plotter_pyleecan.py`),
  from the 5 modules of `Functions/Plot/Pyvista`: static methods first
  (decision), same generator as the FEMM and gmsh objects (dotted
  folders supported). Callers: the `MeshSolution` plots, `Output.plot_B_mesh`
  (`pv_plotter_pyleecan.configure_plot(...)`); legacy paths: deprecated
  aliases.
- `pv.plotting` bug fixed: the pyvista import pass imports the submodules
  loaded on demand by pyvista (`import pyvista.plotting`, `pyvista.core`)
  next to `import pyvista as pv` (`_import_pyvista_submodules`, unit test);
  `test_plot_contour_1group` and `test_import_mesh_unv` pass with each
  backend.
- Group 9 left: `init_fig`, `set_plot_gui_icon`, `get_color_legend_from_surface`
  (to `Machine`, after its config defaults), deprecated `plot_2D_Data` /
  `plot_3D_Data`, `animate_as_gif` (done).
- Checks: `Tests/New/Methods/Mesh` and `Import` 70 passed with each backend;
  class and cross tests as before.

### gmsh interface object (2026-11-21)

- `gmsh_pyleecan` (`Functions_new/GMSH/gmsh_pyleecan.py`), from the 7
  modules of `Functions/GMSH`: static methods only (decision: as close as
  possible to legacy, the object gathers the functions and is improved
  later; the gmsh API is a module, no handler). Same generator as
  `femm_pyleecan` (`femm_object.py`, `InterfaceObject` description:
  folder, class, handler or none).
- Callers: `MagElmer.comp_flux_airgap`, `StructElmer.gen_mesh` call
  `gmsh_pyleecan.draw_GMSH(...)`; the legacy GMSH paths are deprecated
  aliases.
- Checks: gmsh tests (`test_gmsh`, `test_gmsh2`) pass with each backend
  (through the aliases) and legacy; class and cross tests as before.

### FEMM interface object (2026-11-21)

- `femm_pyleecan`, plain helper class written by the functions generator
  (`femm_object.py`) from the 20 modules of `Functions/FEMM`, in
  `Functions_new/FEMM/femm_pyleecan.py` (and `Functions_pydantic`): a
  `femm` sub-package would be the same folder as `FEMM` on Windows, and
  `Classes_new` is rewritten at each run (Phase 2: `pyleecan/femm/`).
- One object per FEMM handler (per parallel worker): `self.handler` is
  the `_FEMMHandler`; `OutMagFEMM.handler_list` holds the objects. The
  functions taking `femm` are methods (`femm.mi_...` ->
  `self.handler.mi_...`, `femm` given to another function -> the
  object), the others static methods; `FEMMError` imported from the
  shared errors.
- Callers (`MagFEMM` methods, geometry `draw_FEMM`, `HoleM61`): calls
  `f(femm, ...)` -> `femm.f(...)`, `_FEMMHandler()` -> `femm_pyleecan()`,
  `femm.mi_...` -> `femm.handler.mi_...` in the functions with a `femm`
  variable; the import of `femm_pyleecan` stays in the function (circular
  import comment). Type hints: `femm : FEMMHandler` -> `femm_pyleecan`.
- The legacy FEMM paths are deprecated aliases (a handler or a
  `femm_pyleecan` object accepted). The GUI (legacy) still uses the
  legacy functions (Step 10).
- Checks: `test_LossFEMM_Prius` runs FEMM through `femm_pyleecan` with each
  backend, up to the known loss error (`KeyError: 'overall'`, #751 open
  point), as before; legacy passes; class, cross, geometry and slot tests
  as before; `ty` geometry 22, magnetics 159 (unchanged); unit tests
  `Tests/New/test_femm_object.py`.

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
  `DataDual.n2dqh` and `DataDual.dqh2n` (new methods, `NEW_METHODS`) build
  the `DataTime` of its time data (`axes_dt`, `values_dt`) and call the
  `DataTime` method: the
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
- [x] `Plot.get_color_legend_from_surface` to `Machine` (done
      2026-11-21: static method, local import in the lamination plots;
      the colors read when called, `legacy_fixes`; `Slot.plot_active`
      and the `SlotM10` / `SlotM11` schematics read `WEDGE_COLOR` /
      `KEY_COLOR` with the `"y"` default the import used to set). Left:
      the `Slot.KEY_COLOR` class constant (CSV) reads the configuration
      without default (as legacy: `KeyError` on a configuration without
      it). The legacy note: the
      module sets default colors in `config_dict` at import
      (`WEDGE_COLOR`, `KEY_COLOR`, read by `Slot.plot_active` and the
      `SlotM10` / `SlotM11` schematics) and the plots import its
      constants (`PHASE_COLORS`, `PLUS_HATCH`, `MINUS_HATCH`): the
      defaults and the constants to move first (with the pyvista /
      plot rework, group 9).
- [x] `GUI.log_error` (decided: in a GUI module, where it is used most;
      done 2026-11-21: `GUI_new/Tools/log_error.py`, the deprecated module
      at the legacy path, the 3 mesh methods `get_logger(self).error(...)`
      by `legacy_fixes`):
      16 GUI modules and 3 mesh export methods (`MeshVTK.save_vtk`,
      `MeshMat.save_vtk`, `MeshSolution.export_to_mat`) call it; moved
      with the GUI in Step 10 (`GUI_new`), the mesh methods logging
      through their logger (Step 9).
- [x] `Structural.conversions` deprecated (2026-11-21): merged into
      `SciDataTool.conversions` (`MERGED_MODULES`, the target being one of
      the merged legacy modules): `xyz_to_rphiz`, `xyz_to_rphiz_field`,
      `rphiz_to_xyz_field` give the same results as the SciDataTool ones
      (not duplicated); `cart2pol` / `pol2cart` (angle from the points)
      added as `cart2pol_points` / `pol2cart_points`, `rphiz_to_xyz` (z kept)
      as `rphiz_to_xyz_3d`; `DimError` from the shared errors. Callers
      (`MeshSolution.get_field`, `SolutionVector.get_field`, `Mode`) import
      the SciDataTool functions; checked against legacy with a script,
      `Tests/New/Methods/Mesh` 42 passed with each backend.

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

- [x] Inventory (2026-11-21): 16 classes have a `logger_name` field
      (Simulation, its models, the outputs, Machine, OptiSolver, Elmer,
      Loss); `Simulation.init_logger` sets per-simulation names
      (`<simulation>`, `<simulation>.Machine`, `.Magnetics`, ...) on the
      simulation, its models and the output, with the per-simulation log
      file handlers; 177 `get_logger()` calls in Methods_new / Functions_new.
- [x] Target (chosen 2026-11-21, maintainer away; to confirm): context
      logger, `classes_common/logger_context.py`. `get_logger(obj)`: the
      object's `logger_name`, else the simulation in progress
      (`logger_context(simulation)`, set by `Simulation.run` around its
      body, the name read when the logger is requested so after
      `init_logger`; nested simulations of a multi-simulation get their
      own context), else the parents (legacy layer, Phase 1), else the
      default logger. Difference with legacy: an object without
      `logger_name` in a simulation logs to the simulation logger instead of
      the logger of its nearest parent with one (`<simulation>` instead of
      `<simulation>.Machine`): same log file.
- [x] Generator pass (`modernize.redirect_get_logger`, methods and
      functions): `x.get_logger()` -> `get_logger(x)`, the imports of the
      legacy function redirected; `wrap_logger_context` for
      `LOGGER_CONTEXTS` (`Simulation.run`; the comments above the first
      statement stay in the block: import guard of `Output` / `XOutput`).
      Unit tests: `Tests/New/test_logger_context.py`.
- [x] `Functions.get_logger` deprecated (`DEPRECATED_MODULES`); the base
      `get_logger` methods (`PyleecanClass`, `PyleecanModel`) use
      `classes_common.logger_context`.
- [ ] Remove the parent fallback and the base method in Phase 2, with the
      parent links (decided 2026-11-21: the fallback stays in Phase 1).
- Checks: class and cross tests as before, Simulation and Machine method
  tests as before; `test_LossFEMM_Prius` (pydantic) writes the
  per-simulation log file with the simulation logger names.

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

- [x] GUI generator (`generate_gui_new.py`, 2026-11-21, called by
      `run_generate_classes` after the functions): `GUI_new` from `GUI` with
      the method pipeline (FEMM object, moved functions, loggers, `Methods`
      imports, `modernize_names`: class and function imports, keyword
      constructors, shared errors), then `MODULE_REDIRECTS`
      (`Classes._ClassInfo`), the `Functions.x` left (`Functions.load`,
      `Functions.Load.import_class`) to `Functions_new.x`, and the GUI
      self-imports to `GUI_new` (`redirect_imports`, relative imports kept
      from the package root). `Ui_*` modules go through the same pipeline;
      `.ui` and `.json` files copied. `Resources` (28 MB) is not copied:
      `__init__.py` (`pixmap_dict`) copied, `pyleecan_rc.py` is a generated
      shim loading the legacy compiled resources by path (without importing
      the legacy GUI package), registered once for both backends (decided
      2026-11-21: the new GUIs use the legacy resources).
      `GUI_pydantic` from `GUI_new` by import rewriting
      (`pydantic_gui_source`). The functions generators redirect the GUI
      imports too (`set_plot_gui_icon`: `GUI_new.Resources` /
      `GUI_pydantic.Resources`). Tests: `Tests/New/test_generate_gui_new.py`.
      Check: the 375 modules of each package import (Qt offscreen); the only
      legacy module still loaded is `Classes._check` (from
      `Functions_new/Load/import_class.py`: `InitUnKnowClassError`).
- [x] (2026-11-22, reviewed) `-1` conventions and the GUI-specific legacy
      idioms: no pass needed in Step 10. No `-1` is assigned to a field in
      `GUI_new`: the `-1` are Qt "no index / no row" values, local default
      sentinels (`set_Wins_wire(Wins_wire=-1)`) or arithmetic. The legacy
      idioms used (`_set_None()` 44 calls, `copy()` 29, `init_dict` 15) are
      provided by both legacy layers (`LegacyClass`, `LegacyModel`) and run
      by the GUI tests, which pass on both backends. Their removal goes with
      the legacy layer (Step 17), as the 14 parent reads (`.parent`).
- [x] (2026-11-22) `import_class("pyleecan.Classes", ...)` in
      `Tools/WTreeEdit/TreeEditContextMenu.py` named the legacy package:
      `redirect_class_loader` (GUI generator) calls the class lookup of the
      backend (`Classes_new._import.import_class(name, prop_name)`,
      `Classes_pydantic._import` in GUI_pydantic); the unused loader import
      of `SWSlot` redirected as well.
- [x] (2026-11-22) Legacy imports left in the new code (functions
      generator): `Load/import_class.py` imports `InitUnKnowClassError` from
      `classes_common.errors` (`LEGACY_CLASS_REPLACEMENTS`),
      `femm_pyleecan` imports `NotImplementedYetError` from the shared
      errors (the method errors redirected in the functions as in the GUI).
      Left: `Functions_new/load_switch.py` (`from ..Classes.import_all import
      *`), a legacy registry imported by no new module: to drop from the
      functions generator (the class lookup replaces it).
- [x] (2026-11-22) `Gen_*` classes generated from `ClassInfo` (min, max,
      description) instead of the CSV files (`Generator/gui_generator.py`),
      so that they survive the Phase 2 removal of the CSV files:
      `write_gen_classes` (GUI generator) writes the 64 modules from the
      `gen_list.json` files, the metadata read in a new process
      (`widget_metadata`: the classes just generated). Checked against the
      modules of the legacy generator: same limits and help texts, except
      `Winding.is_reverse_wind` ("True to reverse...", the description of
      the new class, "1 to reverse..." in the CSV). The units are not used
      by the `Gen_` classes (set by the pages: `lf_x.unit = "m"`).
- [x] (2026-11-22) Validation errors: one contract whatever the backend
      (decided 2026-11-22: conversion in `LegacyModel`). The pydantic legacy
      layer re-raises the `ValidationError` as the legacy errors
      (`legacy_check_error`: `CheckMinError` / `CheckMaxError` /
      `CheckTypeError` with the legacy and dataclass message, named after the
      field also for a nested object; `TypeError` for an unknown constructor
      argument; `AttributeError` with the `FrozenError` message for an
      unknown attribute), the `ValidationError` chained as `__cause__`, on
      construction, assignment, `from_dict` and `model_validate`. The target
      base `PyleecanModel` keeps the `ValidationError` (Phase 2). Contract
      tests: `Tests/New/Cross/test_validation_errors.py` (910 float fields
      with limits or a wrong type: same error class and message on legacy,
      dataclass and pydantic). The error shown on the field: Step 17.
- [x] (2026-11-22) Dataclass backend: the assignment of an unknown
      attribute was accepted silently (`trapeze.unknown = 1`); legacy raises
      `FrozenError`, pydantic `AttributeError`. `LegacyClass` rejects it as
      `FrozenClass` (`AttributeError`, `FrozenError` message; the fields,
      `parent`, the private names and the existing attributes, e.g. a method
      replaced by a mock, can be set). Scan of the `self.x = ...` of
      `Methods_new` that are neither fields nor attributes of their class: 9,
      all false positives (helper exception and Elmer classes, `ModelBH`
      fields of its daughters) except `RuleComplex._set_fct_name`, see below.
- [ ] `RuleComplex(fct_name=...)`: `other_to_P` / `P_to_other` are not set on
      both backends (the inlined `_set_fct_name` is not a wired custom
      setter; legacy sets them in its constructor). Unused by the new
      `convert_to_P` / `convert_to_other` (they call `rule_function_module`):
      drop the two assignments from the method, or declare them if the
      setter is wired.
- [x] `Tests/New/GUI` generated against `GUI_new` / `GUI_pydantic` (2026-11-21:
      alias `backend_gui` in `Tests/New/_backend.py`, the `pyleecan.GUI` and
      `pyleecan.GUI_new` imports and `mock.patch` strings rewritten by the
      test generator). Run per file (the folder in one process crashes Qt
      on garbage collection, before and after; fixed 2026-11-22, see
      below), 6 files in parallel (noisy: the files share
      `Tests/Results`): dataclass 321 -> 453 passed, 222 ->
      122 errors, 25 -> 31 failed; pydantic 339 -> 440 passed, 244 -> 136
      errors, 24 -> 33 failed (legacy GUI -> backend GUI).
- [x] (2026-11-21) `test_DMachineSetup`, `test_SMachineType`, `test_SPreview`:
      the dynamic import `__import__(PACKAGE_NAME + ".GUI.Dialog...")` of
      `SMachineType` loaded the legacy GUI (legacy machine classes:
      `list.index` error), now redirected (`redirect_dynamic_imports`, GUI
      and pydantic GUI); the interface object pass (`redirect_femm_calls`)
      now rewrites the calls in the methods of the classes (GUI widgets) and
      keeps the names of the try-guarded imports bound (`draw_GMSH =
      gmsh_pyleecan.draw_GMSH`: gmsh availability check of `WMachineTable`,
      `NameError` before). The three files pass on both backends.
- [x] (2026-11-21) Hole and slot pages (`test_PHoleM53`, `test_PHoleM52R`,
      `test_PHoleMUD`, `test_SMHoleMag`, `test_PMSlot17`): the GUI caught the
      duplicate errors of the `Methods_new` packages (`Methods_new.slot.Slot.
      SlotCheckError`, not the base of the shared errors raised by the
      classes): the GUI generator imports the shared errors
      (`_redirect_shared_error_imports`). All pass on both backends.
- [x] (2026-11-21) `NewMachine` scenarios (Prius, Benchmark, Benchmark_NS,
      Railway, Zoe) pass on both backends (they hung on a `log_error`
      popup): (1) `DataND._set_values` wired (`WIRED_SETTER_SUBPACKAGES`
      += `scidatatool`, with `Data._set_normalizations`): the values are
      reshaped to the axes as legacy (`comp_mmf_unit` gave a (1600,) array
      instead of (1, 1600)); (2) `femm_pyleecan.as_dict` / `copy` /
      `compare` as the legacy handler (the handlers kept in
      `OutMagFEMM.handler_list` made the HDF5 save fail); (3)
      `modernize.alias_external_class_names`: `from matplotlib.patches import
      Circle` aliased `Circle_patches` (inlined in the `Circle` class it built
      a pyleecan Circle: `Circle(xy=...)` errors of `Shaft.plot`,
      `Circle.get_patches`). Side effects: `Tests/New/Methods` + `Functions`
      + `Plot`: 42 failures fixed per backend (`test_notch`,
      `test_get_polar_eq_SCIM`, the lamination plots), no new failure.
- [x] (2026-11-22) Qt crashes on garbage collection (access violation;
      the legacy GUI as well): `Tests/New/GUI` now runs in one process on
      both backends. Two causes, found with a `gc.collect()` after each
      test: (1) `FloatEdit(parent)` in the Qt Designer modules took the
      parent as its `unit` argument, so the line edit was built without
      parent, owned by Python and by its layout, and deleted twice when the
      dialog was collected (`GUI_LEGACY_FIXES` in `legacy_fixes.py`:
      `unit` keyword-only, applied by the GUI generator); (2) the pages
      replaced after `setParent(None)` were orphans freed by the collector
      inside a later Qt call (`retire_replaced_widgets`: `hide()` +
      `deleteLater()`). Result (whole folder, one process, clean
      `Tests/New/Results/GUI`): dataclass 652 passed, 1 failed, 3 skipped;
      pydantic 653 passed, 3 skipped. The regressions listed before
      (`test_PHoleM53`, `test_PHoleM52R`, `test_SMHoleMag`, `test_PHoleMUD`,
      `test_PMSlot17`, `NewMachine`) all pass.
- [x] (2026-11-22) `test_SMachineType.test_set_p_*` were flaky, legacy as
      well: the random `p` (3 to 99) equal to the default winding `p` (3)
      emits no `valueChanged`, `Zh` is not set. `TEST_FIXES` (test
      generator, `LegacyFix` of the copies): the value is changed when it
      equals the spinbox value. Checked with `uniform` forced to 3: legacy
      3 failed, both backends pass.
- [x] (2026-11-22) The GUI tests that write in `Tests/New/Results/GUI`
      failed when a previous run left its files (`assert not isfile(...)`,
      `FileExistsError`: `SPreview`, `SSimu`, `SWinding`, `NewMachine`):
      `Tests/New/conftest.py` empties `Results/GUI` at the session start
      (xdist controller only).
- [ ] Left: the stator winding flux plot of `SSimu` with one time step
      (`plot_2D_Data` label None, as legacy).
- [x] (2026-11-22, checked) The GUI calls of the logger chain (Step 9) and
      of the moved functions (Step 6, Step 8) are rewritten by the same
      passes: the 14 `get_logger(obj)` calls of `GUI_new` (`SSimu`,
      `DMatSetup`) use `classes_common.logger_context`, and no `GUI_new`
      module imports one of the 80 deprecated alias modules of
      `Functions_new`.
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

- [x] Script classifying every `self.parent` read of `Methods_new` by pattern,
      and by "mechanical" (the container is known from the call sites in
      `Methods_new`) or not: `Generator/ClassGenerator/New/parent_reads.py`
      (`python -m pyleecan.Generator.ClassGenerator.New.parent_reads`), tests
      `Tests/New/test_parent_reads.py`. Report (2026-11-21), reads per
      method of the class folders (the methods moved from Functions
      included; Step 9 removed the logger reads):

      | Package | Methods | logger | label | walk | check | container | other | Mechanical |
      |---|---|---|---|---|---|---|---|---|
      | electrical | 7 | 0 | 0 | 9 | 2 | 2 | 2 | 0 |
      | force | 1 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
      | loss | 26 | 0 | 0 | 50 | 2 | 19 | 0 | 0 |
      | machine | 45 | 0 | 1 | 28 | 39 | 69 | 11 | 0 |
      | magnetics | 3 | 0 | 0 | 2 | 1 | 2 | 0 | 0 |
      | output | 16 | 0 | 0 | 2 | 4 | 17 | 3 | 0 |
      | simulation | 18 | 0 | 0 | 13 | 11 | 7 | 21 | 0 |
      | slot | 151 | 0 | 78 | 0 | 69 | 62 | 57 | 45 |
      | structural | 8 | 0 | 0 | 7 | 3 | 5 | 0 | 0 |
      | **total** | 275 | 0 | 79 | 113 | 132 | 183 | 94 | 45 |

      Columns: `label` = `self.parent.get_label()`, `walk` =
      `self.parent.parent...`, `check` = `self.parent is (not) None`,
      `container` = `self.parent.<attr or method>`, `other` = the parent
      passed on. A method is mechanical when it is called only on a typed
      field of its container (`self.slot.get_surface_active()` in a
      `Lamination` method) or on `self` in its class family, never on an
      unknown receiver: the generator can then pass `self` as the
      container. Findings:
      - Slot: the 45 mechanical methods are the `get_surface_active` /
        `get_surface_opening` / `get_surface_wedges` / `comp_height_active`
        (labels and lamination reads), called by the lamination's
        `build_geometry`. Not mechanical: `plot_schematics` (51, user entry
        points), `build_geometry` (17) and `build_geometry_active` (14)
        (also called on unknown receivers: `slot.build_geometry()` in the
        functions and the tests), `get_Rbo`, `get_is_stator`,
        `is_outwards`. These need the optional argument with its fallback.
      - Simulation models (`run` of Electrical, Force, Loss, ...): pattern 2,
        `self.parent.parent` is the output; the call sites go through
        `Simulation.run`; one pass for all the `run` methods.
      - Loss models (`comp_loss*`): `self.parent.parent` is the simulation
        (machine, output); called by `Loss.comp_all_losses` on the items of
        `model_dict` (unknown receiver for the script): mechanical in fact,
        the container is the `Loss` object.
      - Machine: `Winding` (lamination reads), `Notch` / `Bore` (lamination
        reads), `EndWinding*` (`self.parent.parent` = the lamination),
        `Lamination.plot` and `get_label` (user entry points): optional
        argument with the fallback.
      - Output: sub-outputs (`OutMag`, `OutElec`, ...) read the `Output`.
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

- [x] Shared helper `container_or_parent(obj, container, name, depth=1)`
      (`classes_common/parents.py`, both backends): the given container,
      else the ancestor at `depth` (2 for `self.parent.parent`), None if the
      chain is broken. Tests: `Tests/New/test_container_or_parent.py`.
- [ ] Generator passes, one pattern per increment (method, function and test
      generators), with unit tests and the parity tests unchanged; each pass
      reports the methods given a fallback argument (generated list, copied
      to [Phase 2 deprecations](#phase-2-deprecations)).
  - [x] Pass 1 (2026-11-21), `container_arguments.py`
        (`CONTAINER_ARGUMENTS`, `add_container_arguments`, in the method
        pipeline before the type hints; tests
        `Tests/New/test_container_arguments.py`): the slot methods
        `comp_height_active`, `get_surface_active`, `get_surface_opening`,
        `get_surface_wedges` take `lam: Lamination | Notch | None = None`
        (name decided 2026-11-21: `lam` for the container of a slot, notch
        included)
        (every override of the Slot family, with its docstring entry; the
        overrides reading `self.parent` read `lam = container_or_parent(self,
        lam, "lam")` once). The calls on a slot field of the container pass
        it (`self.slot.get_surface_opening(..., lam=self)` in `LamSlot`,
        `LamSlotM`, `LamSlotWind`, `LamSquirrelCage`,
        `self.notch_shape.get_surface_active(lam=self)` in `NotchEvenDist`);
        the calls on `self` inside these methods pass `lam` on. Other calls
        (`build_geometry_active`, functions, tests) use the fallback.
        `fallback_methods(gen_dict, methods_dir)` lists the methods given the
        argument. Checks: class, cross, Slot and Machine method tests as
        before (2 pre-existing failures: `test_notch`,
        `test_get_polar_eq_SCIM`, `Circle(xy=...)`), `ty` on
        `Methods_new/slot` unchanged (20).
  - [x] Pass 2 (2026-11-21): the models' `run(output=None)` (pattern 2,
        `depth=2`, `caller_value="output"`) for the Electrical, Magnetics,
        Force, Structural and Loss families (`Electrical`, `ElecLUTdq`,
        `Magnetics`, `Force`, `Structural`, `StructElmer`, `Loss`, `LossFEA`):
        `output = container_or_parent(self, output, "output", depth=2)`, the
        guards `self.parent is None` checked only without output (`output is
        None and self.parent is None`, same legacy errors), the assignment
        `output = self.parent.parent` dropped; `Simu1.run_single` passes its
        `output`. The pass also turns a one-line docstring into one with a
        Parameters section. Checks: class, cross, Slot / Machine / Simulation
        method tests as before (pre-existing failures: `test_simu_get_OP_array`,
        `test_VarParamSweep_fct_save_load` (pydantic), the two of pass 1);
        FEMM runs `test_FEMM_closed_slot`, `test_FEMM_LamSlotMultiWind` pass
        on both backends; `ty` unchanged (535 on the six packages).
  - [x] Pass 3 (2026-11-21): `Simu1.run_single(output=None)` (the output
        is the parent), `Simulation.run` passes its `results`
        (`ContainerArgument.callers`: explicit call sites on `self` passing
        a local). Checks: class, cross, Simulation method tests as before,
        FEMM run on both backends.
  - [x] Pass 4 (2026-11-21): the loss models' `comp_loss`,
        `comp_loss_freq`, `comp_loss_time`, `comp_loss_value` take `loss`
        (their `Loss` object, depth 1) and `output` (depth 3), given by
        `Loss.comp_all_losses` and `LossFEA.run` in their loops over
        `model_dict`. The pass now supports several container arguments per
        method (the deepest first; the chains it rewrites are not rewritten
        again), loop variables over a list or dict field as receivers, one
        docstring edit for all the arguments, `pass` for a dropped
        assignment alone in its block. `comp_coeff` left to the fallback (a
        local named `loss` in two of them; `self.parent.parent.machine` in
        `LossModelProximity` / `LossModelWinding`: Step 16). Checks: class,
        cross, method / function / plot tests as before; loss validation
        tests as before (`test_LossFEMM_Prius`: the known `KeyError:
        'overall'`, after FEMM and the loss models ran).
  - [x] Pass 5 (2026-11-21): `Slot.get_Rbo`, `get_is_stator`, `is_outwards`
        take `lam` too (added to the pass 1 spec): the pass 1 methods pass
        it on (90 `get_Rbo(lam=lam)`, 59 `is_outwards(lam=lam)`); the 467
        other calls in the slot methods (not given `lam`) use the fallback.
        Checks: as before; FEMM runs, `test_SWSlot`, `test_new_machine_Railway`
        on both backends; `ty` on `Methods_new/slot` unchanged (20).
  - [x] Pass 6 (2026-11-21): the slot geometry (`build_geometry`,
        `build_geometry_active`, `get_surface_wedge`) takes `lam` (the
        laminations pass `self`, the slot methods pass theirs on). Methods
        of `Methods_new` reading a parent: 275 -> 198 after passes 1-6
        (labels 79 -> 20, walks 113 -> 65, container reads 183 -> 156).
        Checks: as before; FEMM runs and GUI scenarios on both backends;
        `ty` on the slot package unchanged.
  - [x] (2026-11-22) No pass left: review of the remaining candidates
        (methods with a call site knowing the container,
        `parent_reads.classify_methods_new`; 198 methods, 0 mechanical):
        - Winding family (`Winding` 7, `WindingUD` 5): the lamination values
          are already arguments (`comp_Ntsp(Zs)`, `comp_connection_mat(Zs,
          p)`), the parent read only when they are omitted; the calls of
          `LamSlotWind` pass them. A `lam` argument would add nothing.
        - `Conductor`, `CondType22`, `EndWinding*`: read the winding and the
          lamination (`self.parent.Ntcoil`, `self.parent.parent.slot`), no
          call site in `Methods_new` with both: Step 16.
        - The inputs' `gen_input` (pattern 2, `simu` and `output`, called by
          `Simu1.run_single`): four different shapes (`isinstance` guard on
          the parent, base calls through the class `InputVoltage.gen_input(
          self)` / `super(type(self), self)`, the output read through a local
          `simu.parent`), not the rewritten pattern: by hand, Step 16.
        - GUI: the calls of the container-argument methods are on laminations
          (`get_Rbo`, `build_geometry` of `Lamination`) or the simulation,
          except `DXF_Slot` (`slot.get_surface_active()` with the lamination
          in a local `lam`): one site, by hand in Step 17.
  - [ ] Left for Step 16 (not mechanical): the `plot_schematics` of the
        slots (51, user entry points, no caller with the container), the
        machine package (winding, conductor, notch, bore, end winding: user
        entry points and calls on unknown receivers), the inputs'
        `gen_input`, the `comp_coeff` of the loss models, the sub-outputs
        reading the `Output`, the optimization and multi-simulation walks.
- [x] Report the reads left for Step 16: `parent_reads.py` (table above
      for the first run; after passes 1-6: 198 methods, see pass 6).

## Step 12: freeze

- [x] (2026-11-22) The "dynamic_imports", "loaders" and "static_imports"
      passes also run in the method generator (`modernize_names`): the class
      loads of `Methods_new` are static local imports under a guard comment
      (`modernize.LOCAL_IMPORT_GUARD`, "Local import: avoids circular
      imports"), which the class generator keeps local
      (`_has_method_body_import_guard`; without it the imports were hoisted
      and made import cycles). `_static_local_class_imports` accepts the
      legacy normalization names (`Norm_ref` -> `NormRef as Norm_ref`), and
      `_drop_guarded_header_duplicates` removes a guarded local import the
      class header already makes. Also: the method errors imported from the
      shared errors (19 modules `from ....Methods import ParentMissingError`),
      the load and save functions no longer deferred (`VarLoad` imported the
      legacy `Functions.load.load_init_dict`, which loads legacy classes),
      `load_switch.py` (legacy class registry) dropped from the functions
      generator. Generated classes: unchanged except the guard comment lines
      (68 methods) and one redundant local import of `Slot` in `SlotUD2`
      removed; `VarLoad` imports the new loader. `Methods_new`: no
      `import_class("pyleecan.Classes", ...)`, no legacy import left, except
      two dynamic imports `__import__("pyleecan.Classes.Norm_vector")` in
      `Data1D.get_values` / `DataLinspace.get_values` (the local name `module`
      is reused, the pass skips it; the class generator converts them): by
      hand after the freeze.
      The "normalizations" pass stays in the class generator: in
      `Methods_new` the normalization classes keep their legacy local names
      (`Norm_ref`), bound to the new classes.
- [ ] Remove the compatibility shim of the class generator
      (`_read_method_source`: `to_legacy_names`). Tried 2026-11-22: without
      it the generation fails (the normalization rename pass rejects the
      renamed imports: "Cannot safely rename a non-normalization import";
      the relocation of the class imports is not idempotent:
      `material.material.material`). The passes of the class generator
      assume the legacy names: removing the shim means reworking them. Not
      blocking the freeze: the class generator reads the frozen
      `Methods_new` through the shim, as long as the hand-written code keeps
      the forms it translates (imports of `Classes_new` / `Functions_new`).
- [x] (2026-11-22) No legacy object built in `Methods_new`:
      `SlotUD2._set_split_active_surf_dict` and `VarLoad._set_OP_matrix` use
      the class lookup of the backend (`Classes_new._import.import_class`) and
      `Functions_new.load.load_init_dict`.
- [x] (2026-11-22) Parity baseline, `Tests/New/Methods` per package (and
      the legacy `Tests/Methods` as reference), after the Step 12 passes:

      | Package | legacy | dataclass | pydantic |
      |---|---|---|---|
      | Converter | 49 passed | 49 passed | 49 passed |
      | Frame | 5 passed | 2 passed, 3 failed | 2 passed, 3 failed |
      | Geometry | 282 passed | 282 passed | 282 passed |
      | Import | 28 passed | 28 passed | 28 passed |
      | Machine | 79 passed | 79 passed | 79 passed |
      | Mesh | 42 passed, 6 skipped | same | same |
      | Simulation | 43 passed, 4 skipped | 42 passed, 1 failed | 41 passed, 2 failed |
      | Slot | 1052 passed | 1052 passed | 1052 passed |

      Failures: `FrameBar.comp_surface_*` call the legacy custom getter
      `self._get_Rint()`, absent from the new classes (Step 13);
      `test_simu_get_OP_array` (both: a list given to `OP_matrix`, the
      legacy setter converted it) and `test_VarParamSweep_fct_save_load`
      (pydantic: `XOutput.output_list` with None), known since Step 11.
- [ ] Compare the method results between backends (Step 4 item): the tests
      above check each backend against the expected values; a direct
      comparison of the outputs is left to Step 18.
- [x] (2026-11-22) Freeze mechanism (decided 2026-11-17: all at once, since
      Steps 13–17 cover every package): all 19 sub-packages in
      `FROZEN_PACKAGES` (`generate_methods_new.py`); the hand-written modules
      in `HAND_WRITTEN_FUNCTION_MODULES` (`generate_function_new_classes.py`,
      decided 2026-11-22: the parent readers `check_parent.py`,
      `get_logger.py`, `FEMM/femm_pyleecan.py`; the functions generator
      keeps writing the others and the deprecated aliases, and checks that
      the listed modules exist); `GUI_new` frozen (`GUI_NEW_FROZEN` in
      `generate_gui_new.py`: only its `Gen_*` modules, generated from
      `ClassInfo`, and `GUI_pydantic` are written). Tests:
      `Tests/New/test_freeze.py`; checked by hand: a marker added to a
      module of each frozen area survives the three generators.
- [x] (2026-11-22) Full regeneration: all generated files unchanged by the
      freeze.
- [x] (2026-11-22) CLAUDE.md: `Methods_new`, `GUI_new` and the hand-written
      `Functions_new` modules edited by hand; the class generator still reads
      `Methods_new` (through the shim).
- [ ] After the freeze, by hand: the two dynamic imports
      `__import__("pyleecan.Classes.Norm_vector")` of `Data1D.get_values` /
      `DataLinspace.get_values` (static local imports); the `DXF_Slot`
      container call (Step 17).

## Step 13: custom property setters and getters

Legacy classes with their own property setter or getter methods, inlined in
the new classes but not wired to the fields (a dataclass or pydantic field has
no property). The `slot` ones (`SlotW11`/`SlotW11_2`/`SlotW23._set_W3`,
`SlotUD2._set_split_active_surf_dict`) are wired by the legacy layers
(`WIRED_SETTER_SUBPACKAGES`, `classes_common/custom_setters.py`).

- [x] (2026-11-22) `ParamExplorer._set_getter` / `_set_setter`,
      `DataKeeper._set_keeper`, `VarLoad._set_OP_matrix`: wired by the legacy
      layers (`WIRED_SETTER_SUBPACKAGES` += `simulation`) and rewritten by
      hand in `Methods_new`: the function setters only expand the `"simu.x.y"`
      path into the lambda source (`classes_common.functions.
      legacy_function_source`) and assign the field, which keeps a
      `SourceFunction` (lambda source, or a `.py` path, `"<PARAM_DIR>/..."`
      wildcards resolved by `resolve_wildcard_path`; `np`, `sqrt`, `pi` usable
      in the lambdas); `_set_OP_matrix` assigns the field (the layer validates
      it and sets the parent). The pydantic constructor validates the other
      fields first and then assigns the custom-setter fields through their
      setter (as the legacy constructor).
      Found on the way (`test_copy_out` and `test_VarParamSweep_fct_save_load`
      now pass on both backends):
      - The parent links are set only on the fields holding Pyleecan objects
        (`holds_pyleecan_objects`): `ParamExplorerSet.value` (`list[Any]`)
        set the parent of its `InputCurrent` items (TypeError of the parent
        rules), the legacy setters did not.
      - The dumps in a field of plain values (`list[Any]`, e.g.
        `OutMagFEMM.handler_list`) are loaded on both backends
        (`load_serialized_items` in `LegacyModel`); the class lookup loads the
        support class `_FEMMHandler` (`class_lookup.SUPPORT_CLASSES`).
      - `LegacyModel`: a list of objects accepts None items, as the legacy
        setters (`XOutput.output_list = [None] * nb_simu`).
      Tests: `Tests/New/Classes/test_custom_setters.py`.
- [x] `DataND._set_values`, `Data._set_normalizations` (2026-11-21): wired by
      the legacy layers (`WIRED_SETTER_SUBPACKAGES`: `scidatatool`).
- [x] (2026-11-22, checked) `DataND._get_field` / `_get_freqs`,
      `Winding._get_phase_id`: not property getters, private methods called
      explicitly; nothing to do.
- [x] (2026-11-22) `FrameBar.comp_surface_bar` called the legacy property
      getter `self._get_Rint()` (AttributeError): `self.Rint` (hand edit).
      `Tests/New/Methods` per package now passes on both backends as legacy
      (1580 passed).
- [x] `RuleComplex._set_fct_name` (2026-11-21): no longer needed, the
      conversions read the rule functions from the static registry when
      they run (`legacy_fixes`: `convert_to_P`, `convert_to_other`).

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

- [x] (2026-11-22) Methods of the daughters not declared on the base class:
      declared for the type checkers only (`TYPE_CHECKING_MEMBERS`, class
      generator: an `if TYPE_CHECKING:` block of the base class body, methods
      with generic arguments, attributes as properties so that a checker
      does not take them for dataclass fields; nothing at runtime, Python
      3.14 skips the block): `Machine` (`stator`, `rotor`), `Lamination`
      (`winding`), `Data`, `Line`, `Arc` (`comp_radius`, added with the
      geometry review), `Solution`, `Mesh`, `Simulation` (the
      models of `Simu1`), `ImportMatrix`, `OutInternal`. Test:
      `Tests/New/test_type_checking_members.py`.
- [x] (2026-11-22) Optional fields, first part: a field whose default is an
      object or a container (empty CSV value) is no longer annotated
      `X | None` (`machine: Machine`); the legacy layers still accept None.
- [x] (2026-11-22) Optional fields used without check, the rest (fields
      defaulting to None): explicit check raising the new shared
      `FieldMissingError` (`classes_common/errors.py`, written by the class
      generator next to `ParentMissingError`; message "`<Class>.<field>` is
      None: <what is missing>") instead of the `AttributeError` /
      `TypeError` on None. Only the error type changes, nothing that worked
      breaks. 29 methods: `OutMag.Phi_wind` / `B` / `meshsolution` /
      `axes_dict` / `internal`, `OutElec.Us` / `OP` / `PWM` / `axes_dict`,
      `OutForce.AGSF` / `Rag`, `OutGeo.stator` / `rotor` / `axes_dict`,
      `OutGeoLam.BH_curve`, `Simulation.mag` / `elec`, `MeshSolution.group`
      (loss models), `OutLossModel.coeff_dict`, `LUT.simu.var_simu`,
      `LUT.get_eec()` (`EEC_SCIM.update_from_ref`); `LUTdq.comp_MTPA` reads
      the equivalent circuit once. `ref_simu` of the
      `generate_simulation_list` methods (VarSimu, VarParamSweep,
      VarLoadCurrent, VarLoadVoltage) is a required parameter (its None
      default always failed; `VarSimu.run` passes it). Existing checks (`ValueError` / `Exception` of the
      loss models) kept. Left: fields of objects built just before
      (`ElementMat.indice` in `get_FEMM_mesh_results`, `DataND.axes` of a
      `dqh2n` result), local variables and matplotlib returns (review list).
      Test: `Tests/New/test_field_missing_error.py`.
- `ty` on `Methods_new` (2026-11-22): 989 at the start of Step 14 -> 758
      (annotations) -> 620 (base class declarations). By rule:
      unresolved-attribute 190, invalid-argument-type 175, not-subscriptable
      75, invalid-return-type 53, unsupported-operator 36, unknown-argument
      25, invalid-assignment 24. Then -> 580 (explicit `SourceFunction` in
      the VarSimu / VarLoad methods) -> 548 (`OutLossModel` operators).
      Largest groups left: `DataND` (49, mostly the too narrow hints of the
      SciDataTool plot functions), `EEC_SCIM` (30), `MagElmer` (27),
      `OptiGenAlgNsga2Deap` (26), `MagFEMM` (26), `LUTdq` (22). Then -> 465
      (`FieldMissingError` checks) -> 464 (required `ref_simu`) -> 452
      (implicit `None` returns) -> 439 (geometry review).
- [x] (2026-11-22) Implicit `None` returns (12, none left), by case:
      - unreachable last case written as `else` (no behaviour change):
        `Segment.intersect_line` (`inter_line_line` returns 0, 1 or 2
        points), `LamSlotMag.get_magnet_by_label` (both matrices None
        returned first), `SlotW23.get_H1` (second `H1_is_rad` test dropped);
      - missing `return` of the legacy (fixed, the value was lost):
        `LamSquirrelCage.plot_schematics_scr` (`is_default`),
        `HoleM52R.plot_schematics` (the two recursive calls, and
        `return fig, ax` at the end, as `HoleM52`);
      - unsupported case, explicit error instead of None:
        `SlotW14` / `SlotW29.comp_surface_opening` / `comp_surface_wedge`
        (`wedge_type` other than 0 and 1: `NotImplementedError`, as
        `Slot.get_surface_wedges`), `SlotW15.comp_surface_opening` (inward
        slot: `S15InnerError`, as `SlotW15.check`),
        `HoleUD.comp_surface_magnet_id` (index without `magnet_<i>` key:
        `ValueError`);
      - None kept, typed: `Frame.plot` returns `tuple[Figure, Axes] | None`
        (a frame without height is not plotted).
      Test: `Tests/New/test_implicit_none_returns.py`.

Review list by package (behaviour or class definition to decide):

- Geometry:
  - [x] (2026-11-22) `get_patches` (Circle, PolarArc, SurfLine, Trapeze):
        `"--" in edgecolor` after a defaulting that ty could not follow, one
        `if edgecolor is None:` (same behaviour);
  - [x] (2026-11-22) `Segment.intersect_line` implicit `None` return;
  - [x] (2026-11-22) `SurfLine.get_patches` without lines returned a bare
        `Polygon([])` for `list[Polygon]` (and an empty `Polygon` raises
        `ValueError`): returns `[]`;
  - [x] (2026-11-22) also in the package: `Arc` / `Segment.intersect_obj`
        (`comp_radius` of the daughters: declared on `Arc` in
        `TYPE_CHECKING_MEMBERS`, `cast` after `other.is_arc()`),
        `Surface.draw_FEMM` (`FEMM_dict`, and `BC_dict` when a line has a
        boundary condition, `None` defaults: `ValueError`). `ty` clean on
        `Methods_new/geometry`. Test: `Tests/New/test_geometry_review.py`.
- Slot:
  - [x] (2026-11-22) implicit `None` returns: `SlotW14`/`SlotW15`/`SlotW29.comp_surface_opening`,
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
  - [x] (2026-11-22) implicit `None` returns: `Frame.plot`, `LamSquirrelCage.plot_schematics_scr`,
        `LamSlotMag.get_magnet_by_label`;
  - [ ] `LamSlotWind.comp_mmf_unit`: lists given to ndarray fields of `Data1D`;
        `LamSlotWind.plot`: lists for `FancyArrowPatch` positions (tuple);
        `Machine.plot_anim_rotor`: `Patch.xy`.
- Simulation:
  - [ ] `ParamExplorer` (`getter`, `setter`), `DataKeeper` (`keeper`): str
        given to callable fields (Step 13);
  - [ ] `VarParamSweep.generate_simulation_list`: `init_dict=` constructor
        argument (legacy layer only);
  - [x] (2026-11-22) optional fields used without check:
        `VarSimu.set_reused_data` (`output.mag.internal`,
        `output.simu.elec`): explicit errors; `generate_simulation_list`:
        `ref_simu` required;
  - [ ] `Input.comp_axis_*`: `int | None` periodicities compared;
  - [ ] `InputCurrent.gen_input`: lists given to ndarray fields;
        `get_ref_simu_index`: `int | None` returned.
- Loss:
  - [ ] optional fields used without check: `LossModelBertotti` /
        `LossModelSteinmetz.comp_coeff` (`mat_type.mag.LossData.get_data`),
        `Loss.comp_axes` (`output.mag.get_meshsolution()` returns
        `MeshSolution | None`), `Loss.comp_all_losses` (`axes_dict=None`
        parameter; `MeshSolution.group` checked since 2026-11-22);
  - [ ] private matplotlib `Axes._get_lines` (`comp_coeff` plots);
  - [ ] `LossFEA.run`: ty narrows `self.model_dict` to the type of the dict
        literal assigned, then rejects `LossModelMagnet` (ty quirk, field typed
        `dict[str, LossModel]`).
- Output:
  - [x] (2026-11-22) `OutLossModel.__add__`/`__radd__`/`__sub__`/`__rsub__`:
        `other: OutLossModel | dict | int` (0: `sum()` start value, returns
        self; another int: TypeError), `isinstance` branches instead of
        `try`/`except AttributeError`. Kept from legacy: `0 - model` returns
        `model` (not its opposite);
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
  - [x] (2026-11-22) rule functions: `self` -> `rule` (Step 8 item).
  - [x] (2026-11-22) `LUTdq.comp_MTPA` (Step 8 item): written for an old
        vectorized EEC API (`comp_parameters(machine, OP, Tsta, Trot,
        Id_array, Iq_array)` returning the parameters, `solve(eec_param)`);
        the current `EEC_PMSM.comp_parameters()` / `solve()` take one
        operating point from the EEC fields. Deprecated (decided): the
        method warns (`DeprecationWarning`), removed in Phase 2 with its
        alias `Functions.Electrical.comp_MTPA`. Test:
        `Tests/New/test_comp_mtpa_deprecated.py`.
  - [ ] `path_tools.rel_file_path` (Step 8 item): decision of the maintainer.
- [ ] Complete the type hints of the utility functions (from the Step 8 draft).
      `ty` on `Functions_new`: 510 (2026-11-22) -> 357 (SciDataTool plot
      fixes).
  - [x] (2026-11-22) legacy bugs of the Functions modules fixed by the
        functions generator: `FUNCTION_LEGACY_FIXES` (`legacy_fixes.py`,
        {module path in Functions: fixes}, applied when the module is
        read). SciDataTool `plot_2D` / `plot_3D` / `plot_4D`: figure built
        when no axes are given (a figure without axes left `ax` None),
        taken from the axes when only the axes are given (`fig.savefig` /
        `show` / `colorbar` on None); `plot_3D` stem: `matplotlib.cm.get_cmap`
        (removed in matplotlib 3.9) -> `matplotlib.colormaps.get_cmap`;
        `ax.xscale` / `yscale` (AttributeError) -> `set_xscale` /
        `set_yscale`; `ax.zscale("log")` removed (no such method, and Zdata
        is already in dB). Test: `Tests/New/test_function_legacy_fixes.py`.
  - Left in the plots (matplotlib typing): `Axes3D` members on `ax: Axes`
    (3D plots), `Axes.get_figure()` typed optional, `set_xlim` with lists.
  - [x] (2026-11-22) `femm_pyleecan` (hand-written) 68 -> 7: `get_mesh_param`
        `label_dict: dict` (it said `str`), `lam_mesh_dict = {}` without
        lamination (was None); the drawing path takes the `OutElec`
        currents as `DataND | None` (passed through, not used to draw; the
        update functions keep `ndarray`), `lam_dxf: DXFImport | None`,
        `comp_FEMM_Phi_wind -> np.ndarray`, `_get_radius_boundary` on
        `Lamination`; wedge without material: `FieldMissingError`.
        `TYPE_CHECKING_MEMBERS`: `Lamination` (`slot`, `get_Zs`,
        `get_magnet_number`, `get_hole_list`), `Conductor`
        (`comp_surface_active`), `Notch` (`get_key_Ox_radius`);
        `LamSlot` / `LamSlotMulti.get_Zs -> int` (was `float`). Left: the
        legacy `is_eddies = 0` given as bool, `Lamination(init_dict=...)`
        (`init_dict` item of Step 14), `comp_periodicity_geo` typed
        `int | None`. `ty` on `Functions_new` 357 -> 265.
  - [x] (2026-11-22) `gmsh_pyleecan` 52 -> 27: wrong documented types
        overridden (`type_hints.py`): `get_air_box(machine: Machine)` (said
        `float`), returns of `_find_lines_from_point` (list),
        `_find_point_tag` (`int | None`, x, y), `_find_points_from_line`
        (list); `Surface` declares `get_lines` / `comp_surface` of its
        daughters (`TYPE_CHECKING_MEMBERS`). Left: the nested gmsh dicts
        (untyped values: `in` and `update` on unions). gmsh tests 18
        passed. `ty` on `Functions_new` 265 -> 237.
  - [x] (2026-11-22) SciDataTool and Save utilities, 237 -> 206: overrides
        (`type_hints.py`) for wrong documented types
        (`change_referential_waveform(angle0: ndarray)`, `save_json`
        `class_to_split: tuple`), missing returned values
        (`integrate_local_pattern`, `filter_spectral_leakage`) and returns
        depending on flags typed `Any` until overloads (`union1d_tol`,
        `unique_tol`, recursive `split_obj_dict`). Legacy bug
        (`FUNCTION_LEGACY_FIXES`, also applied to the modules read by a
        merge): `n2dqh` without `phase_dir` called `get_phase_dir(Z_n)`
        without the current direction (TypeError, also in legacy): explicit
        `ValueError` (`DataTime.n2dqh` computes `phase_dir` first). The
        overrides do not apply to the annotated legacy signatures (`omp`).
  - Checked, not bugs: `distutils.spawn` (setuptools shim), the
    `matplotlib.cm.get_cmap` import of `init_environment` (fallback of a
    try), `np.trapz` (fallback to `np.trapezoid`).
  - Found: `Tests/New/Functions/test_save_load.py` does not collect
    (`InitUnKnowClassError` no longer in `classes_common.check`), before
    this step too.
  - Left (206 diagnostics, 2026-11-22), not mechanical: the 3D plots read
    `Axes3D` members on `ax: Axes` (~60, local narrowing or an
    `Axes | Axes3D` hint); the rule functions read the fields of the slot
    or hole they just set through `machine.rotor.slot: Slot` /
    `Lamination.hole` (38, local narrowing per rule); the nested gmsh
    dicts (27); the vendored `_swat_em` / `_smoot` (26, not ours); the
    annotated legacy signatures of `omp` (`n_coefs: int = None`, returns);
    `winding_layer.P_to_other` (empty body documented `dict`).
- [x] (2026-11-22) Mark the class-independent functions for
      `src/pyleecan/utils/` (Phase 2). Audit of the `Functions_new` modules
      that stay (not the deprecated modules and aliases, the vendored code,
      the rule functions, the hand-written parent readers): a module is
      class-independent when it imports no pyleecan class, at runtime or for
      typing, directly or through the modules it imports.
  - `utils/` candidates (class-independent): `utils.get_path_binary`,
    `utils.init_environment`, `utils.init_fig`, `utils.labels`,
    `utils.make_ndarray_equal`, `utils.path_tools`, `utils.geometry` (all
    but `cut_lines_between_angles`, which takes `Line` lists),
    `Winding.gen_phase_list`; the SciDataTool math helpers
    (`change_referential`, `conversions`, `derivation_integration`,
    `fft_functions`, `filter_spectral_leakage`, `fix_axes_order`,
    `interpolations`, `nudft_functions`, `set_routines`, `sum_convolution`,
    `sum_mean`, `symmetries`) and plots (`SciDataTool.Plot`: `init_fig`,
    `plot_2D`, `plot_3D`, `plot_4D`).
  - Class-independent, but with a Phase 2 home already decided: the file
    backends `Load.load_array` / `load_hdf5` / `load_json` / `load_pkl`,
    `Save.save_array` / `save_hdf5` / `save_pkl` (load and save classes,
    group 12), `pv_plotter_pyleecan` (interface object, like
    `femm_pyleecan` and `gmsh_pyleecan`).
  - Class-dependent, stay with the classes: `SciDataTool.dqh_transformation`
    (`DataTime` / `DataFreq` helpers), `SciDataTool.is_axes_in_order`,
    `omp` (`Data1D`), `parser` (`RequestedAxis`), `utils.geometry.cut_lines_between_angles`,
    `Save.save_json`, `load` / `save`, `Load.retrocompatibility`,
    `Load.import_class` and `Converter.rule_functions` (loaders),
    `gmsh_pyleecan`.

## Step 16: parent links, second pass

Same signature rule as Step 11 (optional container argument, fallback through
`container_or_parent`); each new site is added to
[Phase 2 deprecations](#phase-2-deprecations).

- [x] (2026-11-22) Remove the reads left by Step 11, package by package (Slot, Machine,
      Simulation, Loss, Output, Optimization). Direct `.parent` reads at the
      start (2026-11-22): `Methods_new` 486 in 202 modules (slot 194, machine
      148, simulation 58, output 26, loss 21, electrical 18, structural 11,
      magnetics 5, optimization 4, force 1), `Functions_new` 7 (the three
      hand-written modules).
  - [x] (2026-11-22) Slot package: 194 -> 0. Same rule as Step 11 (`lam:
        Lamination | None = None`, read once with `container_or_parent`).
        The 56 `plot_schematics*` of the slots and holes (`if self.parent
        is None` / `lam = self.parent` / `self.parent.Rext`; the inner
        `plot_schematics` calls pass `lam` on, the default laminations
        included) and the accessors reading the lamination (Hole
        `get_R_id`, `get_Rbo`, `get_Rext`, `get_is_stator`,
        `build_geometry`, `comp_mass_magnets`, `comp_mass_magnet_id`,
        `comp_volume_magnets`; Slot `get_name_lam`, `get_surface_tooth`,
        `comp_width_opening`; `SlotM17.check`, `comp_height`,
        `comp_surface`, `comp_surface_active`), then the Step 11 pass run
        as a tool on the frozen sources (`add_container_arguments` with the
        two specs below, then `add_type_hints`): every override of the
        family takes `lam` (Slot: the plots, `check`, `comp_height`,
        `comp_surface`, `comp_surface_active`, `get_name_lam`,
        `get_surface_tooth`, `comp_width_opening`; Hole family: the plots
        and the accessors above), the laminations pass `self`
        (`self.slot.comp_surface_active(lam=self)`, the holes of
        `LamHole.build_geometry`, `NotchEvenDist`) and the GUI the
        lamination it holds (54 calls: `lam.slot.check(lam=lam)`,
        `self.slot.comp_surface(lam=self.lamination)`). The `from . import *`
        of the modules edited named (the wildcard kept the class generator
        from inlining them: 20 `check`, 3 ventilations). Checks: class tests
        both backends, Slot / Machine method tests 1131 passed and the
        schematics plot tests 157 passed with each backend, GUI tests of the
        machine setup pages 524 passed with each backend; `ty` unchanged.
  - [x] (2026-11-22) Machine package: 148 -> 0, with the Step 11 pass run
        as a tool (specs per family): `Winding` family `lam` (the
        connection matrix, turns, factors, plots, `WindingUD` imports and
        `init_as_*`; `plot_linear` also `machine`, depth 2, for the window
        title), `Conductor` and `EndWinding` families `winding` and `lam`
        (depth 2), `Skew` `lam` and `machine`, `Bore` and `Notch` families
        `lam`, `Frame` family and `Lamination` family (`get_label`, the
        plots, `comp_mmf_unit`) `machine`. The containers known by the
        callers are passed (the laminations to their winding, the winding
        to its conductor and end winding, the machine to its laminations;
        GUI: `SWinding` (`lam=self.obj`, `machine=self.machine`), `SSkew`,
        the bore pages). By hand: the guards the pass wrote with a shorter
        chain (`lam is None and self.parent is None`: the `EndWinding*`,
        `Skew.comp_angle`). Legacy bug found: `self.get_logger.warning(`
        (missing call, AttributeError instead of the warning) in
        `EndWindingCirc` / `EndWindingRect` and `VarLoad.set_OP_array`:
        `get_logger(self).warning(`. Checks: class tests, Slot / Machine
        method and plot tests (4254 passed with each backend; 3
        pre-existing failures of `test_ICEM_2020`, before Step 16 too:
        `OPdq` rejected by an `OP` field, `test_WindingUD_layer`), GUI tests
        of the winding, skew, bore, bar, conductor, notch and preview pages
        49 passed with each backend.
  - [x] (2026-11-22) Simulation package: 58 -> 0, by hand (the shapes are
        not the pass pattern: `isinstance` guards, walks, base calls):
        - the inputs' `gen_input` (`InputVoltage`, `InputCurrent`,
          `InputFlux`, `InputForce`) and `Input.comp_axes` take `simu` and
          `output` (depth 2); the base calls (`InputVoltage.gen_input(self,
          ...)`, `super(type(self), self).gen_input(...)`) pass them on;
          `Simu1.run_single`, `Force` / `Magnetics.comp_axes` and the GUI
          preview table pass them;
        - `Simulation.run(output=None)`: the given output or the parent,
          else a new `Output` / `XOutput`; it passes its simulation and
          results to `var_simu.run`; `comp_LUTdq` and the NSGA2 evaluation
          pass the output they hold;
        - the multi-simulations take `simu` (`VarSimu.run` /
          `check_param`, `VarParamSweep.check_param`, `VarOpti.run` /
          `check` / `get_full_solver`, `VarLoadCurrent` / `VarLoadVoltage`
          `get_input_list`), the `run` methods also `xoutput` (depth 2);
        - new helper `ancestor_with(obj, attribute, container, name)`
          (`classes_common/parents.py`, with `container_or_parent`; tests in
          `Tests/New/test_container_or_parent.py`): the parent walk of an
          unknown depth, for `OP` / `EEC.get_machine_from_parent`,
          `VarLoad.set_OP_array` (`simu`, the simulation holding the input:
          the parent or its parent) and the `get_elec_datakeeper` of the
          VarLoad family (`simu`, given by `gen_datakeeper_list`). Phase 2
          adds its DeprecationWarning with the one of `container_or_parent`.
        Checks: class tests, Simulation method tests (43 passed, 4 skipped)
        and simulation / preview GUI tests pass with each backend; `ty`
        unchanged.
  - [x] (2026-11-22) Output, loss, electrical, structural, magnetics,
        optimization, force packages: 82 -> 0 (no direct parent read left
        in `Methods_new`):
        - the guards Step 11 kept (`if output is None and self.parent is
          None`): one message -> `if output is None:`, two messages (the
          missing level) -> `container_or_parent(self, None, "simu")`; the
          `else: pass` left by the pass removed;
        - the pass as a tool: the sub-outputs take `output` (`OutElec`
          getters and `store`, `OutMag` `comp_emf` / `comp_power` /
          `comp_torque_MT` / `store`, `OutLoss` getters and plot;
          `OutLossModel` `out_loss` and `output`), `Loss.comp_all_losses`
          `output`, `ElecLUTdq` `simu` (and `output`), `get_slice_model` /
          `MagFEMM.build_meshsolution` and `StructElmer.gen_case` `simu`,
          `Mode` `meshsol`; the calls on a local output pass it
          (`output.elec.get_Is(output=output)`, 21 calls, GUI included);
        - by hand: the loss models' `comp_coeff` (Joule `output`, Winding
          `simu`, Proximity `loss` and `simu`; the conductor's slot and
          turns read on the lamination it comes from), `DriveWave.get_wave`
          (`output`, depth 4, instead of `check_parent(self, 4)`),
          `Structural.comp_axes` (`output` optional), `XOutput.plot_pareto`
          (`solver`, the OptiSolver holding it); the parent of another
          object through the helper (`container_or_parent(machine, None,
          "simu")` in `EEC.comp_fluxlinkage`, the magnet's hole / lamination
          in `MagElmer.solve_FEA`, the problem simulation's output in the
          optimization solvers).
        Checks: class tests; Methods, Plot, Simulation and Functions tests
        4735 passed with each backend; loss validation tests 14 passed
        with each backend; simulation / preview GUI tests pass; `ty`
        unchanged. Failures before Step 16 too (checked on the commit
        before the step): `test_ICEM_2020` (3), `test_post_var_simu`, the
        retrocompatibility `test_save_OPM_retro` / `test_load_opti`, the
        multi-simulation validations (`VarSimu` parent type,
        `XOutput._get_symbol_data_` arguments), the collection of
        `test_save_load` / `test_import_class` (`InitUnKnowClassError`).
        Found: `Loss.run` passes `meshsol=` to `comp_axes`, which
        `LossFEA.comp_axes` does not take (LossFEA overrides `run`).
- [x] (2026-11-22) Function helpers with explicit arguments: `check_parent`,
      `assign_femm_surface`. `femm_pyleecan.assign_FEMM_surface` (and
      `MagElmer.solve_FEA`) read the hole or lamination of a magnet from its
      label (`machine.get_lam_by_label(...)`, `get_hole_list()[R_id]`, as
      `get_obj_from_label`) instead of `mag_obj.parent` / `hole.parent`;
      `check_parent` (no caller left, `DriveWave.get_wave` reads its output
      with `container_or_parent`) is a deprecated alias on
      `container_or_parent` (it warns; Phase 2 register); the deprecated
      `Functions_new/get_logger.py` walks with `container_or_parent`.
- [ ] Tests of a refactored package hand-maintained; numerical parity against
      legacy, from the Step 12 baseline.
  - [x] (2026-11-22) Parity after the Step 16 packages, `Tests/New/Methods`
        per package (both backends the same): Converter 49, Frame 5,
        Geometry 282, Import 28, Machine 79, Mesh 42 (6 skipped),
        Simulation 43 (4 skipped), Slot 1052 passed: as the baseline or
        better (Frame and Simulation failures of the baseline fixed by Steps
        13 and 16). The legacy-derived tests still call the methods without
        the containers (the fallback), so they measure the parity.
  - [x] (2026-11-22) `Tests/New` frozen (decided by the maintainer,
        2026-11-22): `TESTS_NEW_FROZEN` in `generate_test_new_classes.py`,
        the full generation copies nothing (`generate_tests(frozen=False)`
        for the generator unit tests); a change of a legacy test is ported
        by hand. The generator unit tests fixed on the way (stale
        expectations: the backend aliases, the `TEST_FIXES` check on the
        temporary trees).
  - [x] (2026-11-22) `ContainerFallbackWarning` (`PendingDeprecationWarning`)
        emitted by `container_or_parent` / `ancestor_with` when a parent
        link gives the container (stacklevel: the caller of the method).
        First count, `Tests/New` Classes / Methods / Plot / Functions /
        Simulation / GUI on dataclass (5388 passed, the 6 known failures):
        the fallback is used at 281 lines of 86 test modules, and inside
        the library at 608 call sites of `Classes_new` (the `Methods_new`
        calls not passing the container they hold), 11 of `Functions_new`
        (FEMM, GMSH) and 10 of `GUI_new`.
  - [ ] The library calls pass the containers they hold.
  - [ ] The tests pass the containers; `Tests/New` turns the warning into
        an error (except the tests of the fallback itself).
- [x] (2026-11-22) No parent read left in `Methods_new` and `Functions_new`
      outside `container_or_parent` (and `ancestor_with`, its walk of an
      unknown depth); the parent links stay only in the legacy layer.
      Direct `.parent` reads: `Methods_new` 486 -> 0, `Functions_new` 7 ->
      0 (AST count of the `.parent` attributes).
- [x] (2026-11-22) The `GUI_new` calls of each refactored package updated in the same
      increment (slot 54 calls, machine: winding, skew and bore pages,
      simulation: preview table, outputs: simulation page).
- [x] (2026-11-22) `Winding.find_wind_phase_color` as a regular method reading
      the connection matrix (like `get_phase_id`): `find_wind_phase_color(
      self, label, wind_mat=None)` (default `self.get_connection_mat()`),
      the legacy body static as `_find_wind_phase_color(label, wind_mat)`
      (the deprecated alias at the old path calls it; spec `bound` in
      `moved_functions.py`, the methods by hand). `LamSlotWind.plot` and
      `LamSlotMultiWind.plot` call it on the winding when they have its
      matrix, and keep the first phase color otherwise (no winding,
      `WindingSC`: `_find_wind_phase_color(label, None)`). Checks: Machine
      method and plot tests, winding GUI tests with each backend.

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
| `comp_height_active` of the Slot family (36 classes) | `lam` | Step 11, pass 1 |
| `get_surface_active` of the Slot family (38 classes) | `lam` | Step 11, pass 1 |
| `get_surface_opening` of the Slot family (24 classes) | `lam` | Step 11, pass 1 |
| `Slot.get_surface_wedges` | `lam` | Step 11, pass 1 |
| `Slot.get_Rbo`, `Slot.get_is_stator`, `Slot.is_outwards` | `lam` | Step 11, pass 5 |
| `build_geometry`, `build_geometry_active`, `get_surface_wedge` of the Slot family | `lam` | Step 11, pass 6 |
| `run` of `Electrical`, `ElecLUTdq`, `Magnetics`, `Force`, `Structural`, `StructElmer`, `Loss`, `LossFEA` | `output` | Step 11, pass 2 |
| `Simu1.run_single` | `output` | Step 11, pass 3 |
| `comp_loss`, `comp_loss_freq`, `comp_loss_time`, `comp_loss_value` of the LossModel family | `loss`, `output` | Step 11, pass 4 |
| `plot_schematics` (and `_constant_tooth`, `_top_flat`, `_radial`), `check`, `comp_height`, `comp_surface`, `comp_surface_active`, `get_name_lam`, `get_surface_tooth`, `comp_width_opening` of the Slot family | `lam` | Step 16 |
| `plot_schematics` (and variants), `get_R_id`, `get_Rbo`, `get_Rext`, `get_is_stator`, `build_geometry`, `comp_mass_magnets`, `comp_mass_magnet_id`, `comp_volume_magnets` of the Hole family | `lam` | Step 16 |
| `comp_Ncspc`, `comp_Ntsp`, `comp_connection_mat`, `comp_phasor_angle`, `comp_winding_factor`, `plot_linear`, `plot_radial`, `comp_periodicity`, `import_from_csv`, `init_as_*` of the Winding family | `lam` (`plot_linear`: also `machine`) | Step 16 |
| `comp_skin_effect_inductance`, `comp_skin_effect_resistance`, `comp_width_wire`, `comp_height_wire` of the Conductor family; `comp_length`, `comp_inductance` of the EndWinding family | `winding`, `lam` | Step 16 |
| `Skew.comp_angle`, `Skew.plot` | `lam`, `machine` | Step 16 |
| `plot_schematics`, `get_bore_line`, `get_pole_shape`, `is_yoke` of the Bore family; `get_Rbo`, `get_Ryoke`, `get_label`, `is_outwards` of the Notch family | `lam` | Step 16 |
| `comp_height_gap`, `build_geometry_bar` of the Frame family; `get_label`, `plot`, `plot_winding`, `plot_mmf_unit`, `comp_mmf_unit` of the Lamination family | `machine` | Step 16 |
| `gen_input` of the Input family, `Input.comp_axes` | `simu`, `output` | Step 16 |
| `Simulation.run` | `output` | Step 16 |
| `VarSimu.run`, `VarOpti.run` | `simu`, `xoutput` | Step 16 |
| `check_param`, `get_input_list`, `get_elec_datakeeper`, `VarLoad.set_OP_array` of the VarSimu family; `VarOpti.check`, `VarOpti.get_full_solver` | `simu` | Step 16 |
| `OP.get_machine_from_parent`, `EEC.get_machine_from_parent` (no argument: the lookup itself) | `ancestor_with` walk | Step 16 |
| `OutElec` (`get_electrical`, `get_Is`, `get_Us`, `get_Jrms`, `store`), `OutMag` (`comp_emf`, `comp_power`, `comp_torque_MT`, `store`), `OutLoss` (`get_loss_density_ag`, `get_meshsolution`, `get_power_dict`, `plot_losses`), `Loss.comp_all_losses`, `Structural.comp_axes`, `DriveWave.get_wave` | `output` | Step 16 |
| `OutLossModel.get_loss_scalar`, `get_mesh_solution` | `out_loss`, `output` | Step 16 |
| `ElecLUTdq.comp_LUTdq`, `solve_MTPA`, `solve_power`; `Magnetics.get_slice_model`, `MagFEMM.build_meshsolution`, `StructElmer.gen_case` | `simu` (`solve_*`: also `output`) | Step 16 |
| `comp_coeff` of `LossModelJoule` / `LossModelWinding` / `LossModelProximity` | `output` / `simu` / `loss`, `simu` | Step 16 |
| `get_shape_pol`, `get_shape_xyz`, `plot`, `plot_animated` of `Mode` | `meshsol` | Step 16 |
| `XOutput.plot_pareto` | `solver` | Step 16 |
| Parent of another object (`EEC.comp_fluxlinkage`, `MagElmer.solve_FEA`, the optimization solvers) | `container_or_parent(obj, None, ...)` | Step 16 |

Full list: `container_arguments.fallback_methods(gen_dict, Methods_new)`.

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
| `Plot.Pyvista.get_arrows_plt`, `Geometry.create_surface`, `FEMM.comp_FEMM_Jcus`, `FEMM.create_FEMM_bar`, `getattr_recursive`, `short_filepath` | none (dead code) | Step 8 group 1 |
| `Converter.MotorCAD.slotW23_H1` | none (not used by the rules) | Step 8 |
| `Converter.Utils.EquivalentError` | none (unused error) | Step 8 group 1 |
| Logger parent fallback (`classes_common.logger_context.get_logger`) | removed with the parent links | Step 9 (kept in Phase 1) |
| `labels`, `path_tools`, `init_environment`, `make_ndarray_equal`, `get_path_binary` (modules) | the same modules in `utils` | Step 8 group 13 |
| `GUI.log_error` (module) | `Tools.log_error` of the GUI package | Step 8 group 13 |
| `init_fig` (module) | `utils.init_fig` | Step 8 group 9 |
| `Plot.set_plot_gui_icon` (module) | `Tools.set_plot_gui_icon` of the GUI package | Step 8 group 9 |
| `Plot.get_color_legend_from_surface` | `Machine.get_color_legend_from_surface` | Step 8 group 9 |
| `LUTdq.comp_MTPA` (and its alias `Electrical.comp_MTPA`) | none (older EEC API, does not run) | Step 15 |
| `check_parent` | `classes_common.parents.container_or_parent` | Step 16 |

- [ ] Decide which other legacy behaviours removed with the legacy layer need
      a deprecation period (`-1` default, `None` everywhere, `as_dict` /
      `from_dict` / `copy` / `compare`, `init_dict=` / `init_str=`, legacy
      class names when loading files) and add them here.

## Infrastructure

- [ ] CI running the suite once per backend (no CI configuration in the
      repository yet): `pytest Tests/New/Classes --backend=dataclass` and
      `--backend=pydantic`, plus `Tests/Classes`.

## Phase 2

- [ ] FEMM 5.0 instead of FEMM 4.2 (noted 2026-11-21, PLAN.md
      Challenges): new `femm_pyleecan.handler` (today the COM interface
      `win32com` on Windows, wine on Linux); parallel runs on Linux;
      processes instead of the threads of `solve_FEMM_parallel`
      (`multiprocessing.dummy.Pool`): one FEMM instance per process, the
      inputs and results pickled (the `femm_pyleecan` objects are per
      worker already).
- [ ] Discuss how to keep the git history when only one backend is kept
      (PLAN.md Challenges): the inlining of the methods into the class
      modules, rename-only commits, the old path -> new location mapping
      (noted 2026-11-21).
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
