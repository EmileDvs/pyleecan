# Backlog of the class refactoring

Detailed tasks of the remaining steps of [PLAN.md](PLAN.md), with the findings
and the reference data they need. A task done is checked here and summarized
in the [CHANGELOG](CHANGELOG.md); the step checkbox of PLAN.md is checked
when all its tasks are done.

Modes: **generator** tasks change `Generator/ClassGenerator/New/` (never the
generated folders); **frozen** tasks edit `Methods_new` / `Functions_new` by
hand, after the freeze (Step 11).

## Step 5: legacy bugs

Found by `ty` on the first type hint pass. These lines raise an exception
when they run; they are fixed in the generator (method generator pass, or
an override of the legacy source), each listed under "Fixed" in the
CHANGELOG. Fixes change the behaviour against legacy only where legacy
raised an error.

- [ ] `VectorField.get_harm_xyz_along`: `pol2cart` not imported (NameError).
- [ ] `EEC_SCIM._comp_flux_mean`: `n2abc(..., n=...)`, `n2abc` has no `n`
      parameter (TypeError).
- [ ] `DataND.compare_along` / `compare_magnitude_along` /
      `compare_phase_along`: `get_interpolation` called without its `index`
      argument (TypeError; SciDataTool internals).
- [ ] `ModelBH.fit_model`: the last `else` branch calls `self.BH_func(H, Bs, a)`
      with undefined `Bs` and `a` (NameError), and `new_BH` is unbound there.
- [ ] `ConvertMC.convert_slot_to_other` / `convert_slot_rotor_to_other`: the
      `else` branch builds its error message with `name_slot` before it is
      assigned (UnboundLocalError instead of NotImplementedError).
- [ ] `BoreSinePole.get_bore_line`: `raise ()` (TODO in the legacy code: a
      TypeError instead of an explicit error).
- [ ] To check (bug or `ty` limit):
  - `ElecLUTdq.run`: `Pjoule`, `Pstator`... given to a constructor without
    these fields;
  - `OP.get_OP_array`: `append` on a tuple;
  - `NotchEvenDist.get_notch_desc_list`: `<` between str and int.

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
(environment); `check_parent` goes with the parent links (Step 15). These
decisions may be revised by the per-module plan of Step 8.

## Step 7: integrate the open legacy pull requests

The legacy folders (`Classes`, `Methods`, `Functions`, the CSV files) are
never edited on this branch; they change only through these merges. The
generators then carry the changes to the new code.

- [ ] #751 (branch `loss_fea`, last commit "Test comparing loss time and
      freq"): finish the remaining work (to detail).
- [ ] #748: merge, regenerate, check.
- [ ] #749: merge, regenerate, check.
- [ ] #751: merge, regenerate, check.
- [ ] #752: merge, regenerate, check.

For each merge:

- conflicts resolved in the generators, never in the generated folders;
- new CSV classes placed in their sub-package (moved physics classes:
  `class_generator`), new legacy functions handled by the functions
  generator, new tests by the test generator;
- `Tests/Classes`, `Tests/New/Classes` (both backends), `Tests/New/Cross` and
  the method tests of the packages touched pass;
- `HINTED_SUBPACKAGES` coverage and `ty` diagnostics of the packages touched
  updated in the Step 13 table; new legacy bugs added to Step 5.

## Step 8: refactor the remaining `Functions` modules

Goal: drastically reduce the utility functions left for Phase 2. Each module
of `Functions` (outside SciDataTool and the vendored code) gets a target:
moved to a class (`MOVED_FUNCTIONS`), merged with another module, kept as a
utility (`utils/` in Phase 2), or removed (dead code, deprecated first).

- [ ] Plan per module (given by the maintainer, to be written here).
- [ ] Generator support for the targets the Step 6 mechanism does not cover
      yet (e.g. merging modules, functions moved together as a group).
- [ ] Apply the plan, one module or group per increment: deprecated aliases
      at the old paths, callers in `Methods_new` and `Functions_new` updated,
      test generator redirects, tests unchanged.
- [ ] Type hints drafted for the functions that stay utilities: run the
      `type_hints.py` pass in the functions generator (same rules as the
      methods), report the coverage and the `ty` diagnostics of
      `Functions_new`.

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

## Step 10: parent links, first pass

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
- Step 15 may still narrow a method to plain values where it clearly helps.

- [ ] Shared helper `container_or_parent` (both backends), with unit tests.
- [ ] Generator passes, one pattern per increment (method, function and test
      generators), with unit tests and the parity tests unchanged; each pass
      reports the methods given a fallback argument (generated list, copied
      to [Phase 2 deprecations](#phase-2-deprecations)).
- [ ] Report the reads left for Step 15.

## Step 11: freeze

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
- [ ] Freeze mechanism (decided 2026-11-17: all at once, since Steps 12–15
      cover every package): all sub-packages in `FROZEN_PACKAGES`
      (`generate_methods_new.py`); a list of the hand-written modules in the
      functions generator (`generate_function_new_classes.py`), which keeps
      writing the others and the deprecated aliases.
- [ ] Full regeneration: generated classes unchanged by the freeze.
- [ ] CLAUDE.md: `Methods_new` and the frozen `Functions_new` modules edited by
      hand; which generator modules are still in use.

## Step 12: custom property setters and getters

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

## Step 13: type hints, second pass

Conventions: class annotations use imports under `if TYPE_CHECKING:` (lazy
annotations of Python 3.14, no `from __future__ import annotations`, which the
class generator does not inline); no runtime import, so no cycle and the
backend import rewriting keeps working.

Coverage of the first pass (parameters / returns hinted, `ty` diagnostics):

| Package | Parameters | Returns | ty |
|---|---|---|---|
| geometry | 135/164 | 125/131 | 21 |
| slot | 832/886 | 657/694 | 20 |
| material | 19/19 | 12/12 | 2 |
| machine | 445/458 | 321/337 | 38 |
| simulation | 86/97 | 82/90 | 62 |
| loss | 8/8 | 16/16 | 11 |
| output | 100/123 | 57/80 | 81 |
| optimization | 16/41 | 8/17 | 65 |
| converter | 77/95 | 86/100 | 26 |
| electrical | 35/46 | 41/46 | 143 |
| magnetics | 50/61 | 15/17 | 144 |
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
        given to callable fields (Step 12);
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

## Step 14: utility functions

First audit (2026-11-15, from imports): 26 of the 145 legacy `Functions`
modules are used by a single class (17 after review, Step 6), and 41 modules
are imported by no class, function or GUI module. Step 8 sorts them by
generator; this step finishes by hand what the generator could not do.

- [ ] Finish the module targets of Step 8 that need hand changes.
- [ ] Complete the type hints of the utility functions (from the Step 8 draft).
- [ ] Mark the class-independent functions for `src/pyleecan/utils/` (Phase 2).

## Step 15: parent links, second pass

Same signature rule as Step 10 (optional container argument, fallback through
`container_or_parent`); each new site is added to
[Phase 2 deprecations](#phase-2-deprecations).

- [ ] Remove the reads left by Step 10, package by package (Slot, Machine,
      Simulation, Loss, Output, Optimization).
- [ ] Function helpers with explicit arguments: `check_parent`,
      `assign_femm_surface`.
- [ ] Tests of a refactored package hand-maintained; numerical parity against
      legacy, from the Step 11 baseline.
- [ ] No parent read left in `Methods_new` and `Functions_new` outside
      `container_or_parent`; the parent links stay only in the legacy layer.

## Phase 2 deprecations

Register of what Phase 1 keeps for compatibility and Phase 2 must deprecate
or remove. Every Phase 1 step adding such a compatibility path adds its sites
here.

Parent fallbacks (Steps 10 and 15): in Phase 2, `container_or_parent` raises a
`DeprecationWarning` when the container is not given; a later release removes
the fallback, the parent links, and makes the argument required.

| Method | Container argument | Added in |
|---|---|---|
| (filled by the Step 10 passes) | | |

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
