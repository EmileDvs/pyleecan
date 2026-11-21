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
- Generation of the phase axis.
- **Class generator**: a CSV description ending with a double quote
  produced an invalid attribute docstring (SyntaxError).
- **Functions generator**: a legacy function module deleted upstream no
  longer stays in `Functions_new` and `Functions_pydantic`.
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
| 4. Phase 1 test architecture (`--backend`) | done (method results compared at the freeze, Step 11) |
| 5. `Methods_new` generator and type hints, first pass | done for all packages; legacy bugs found by `ty` to fix |
| 6. Class-specific functions moved to their class | done (3 functions) |
| 7. Integrate the open legacy pull requests (#748, #749, #751, #752) | #751 merged |
| 8. Refactor the remaining `Functions` modules (generator) | to do |
| 9. Logger chain (generator) | to do |
| 10. Parent links, first pass (generator) | to do |
| 11. Freeze | to do |
| 12. Custom property setters and getters (frozen) | to do |
| 13. Type hints, second pass (frozen) | to do |
| 14. Utility functions (frozen) | to do |
| 15. Parent links, second pass (frozen) | to do |

Legacy class tests (`Tests/New/Classes`), with each backend: 2855 passed,
1 failed (`test_copy_out`: custom property setter of `ParamExplorer`, planned
in Step 12). Cross tests (`Tests/New/Cross`): 1405 passed.
