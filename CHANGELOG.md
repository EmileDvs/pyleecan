# Changelog

All notable changes to pyleecan are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The roadmap of the ongoing refactoring is in
[PLAN.md](src/pyleecan/Generator/ClassGenerator/New/PLAN.md).

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
  classes, with snake_case module names and shared errors in
  `Classes_new/_error.py`.
- **`Tests/New`**: copy of the legacy tests targeting the new classes and
  functions; test data gathered in `Tests/Data`.
- **`ClassInfo`** (`Classes_new/_class_info.py`): the class information
  (properties, types, units, min/max, descriptions) is rebuilt at runtime from
  the classes themselves; `Class_Dict.json` is no longer needed.
- **Class sub-packages**: the classes of `Classes_new` are organized in
  lowercase sub-packages following the legacy packages (`geometry`, `machine`,
  `slot`, ...; `Import` becomes `import_data`). The `electrical` (with EEC and
  Drive), `magnetics`, `force` and `structural` (with Mode) modules and their
  child classes are taken out of `simulation`.
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
- Class constants refactored to avoid circular imports; attribute metadata
  (unit, min, max) and descriptions follow the legacy definitions.
- The load function returns objects of the new classes.
- Normalization classes follow the class naming convention (`Norm_ref` ->
  `NormRef`); the legacy names remain accepted when loading files. The
  mapping is defined once in `classes_common.class_lookup`.
- The class generator no longer imports generated code (it read the legacy
  class names from the generated `Functions_new`).

### Fixed

- Generation of the phase axis.

### Status

Phase 1 progress (see [PLAN.md](src/pyleecan/Generator/ClassGenerator/New/PLAN.md)):

| Step | Status |
|---|---|
| 0. Separate the implementations in the generator | done |
| 1. Split the bases (target / legacy layer) | to do |
| 2. Type, min and max validation for dataclasses | to do |
| 3. `Functions_pydantic` | to do |
| 4. Phase 1 test architecture (`--backend`) | to do |
| 5. Package refactor pass (`Methods_new`, no parent links) | to do |
| 6. Remaining utility functions | to do |

Legacy class tests (`Tests/New/Classes`, run on `Classes_new`): 2352 passed,
472 failed. The failures are the type, min and max checks that the
dataclasses do not implement yet (Step 2); `Classes_pydantic` is tested by the
same suite from Step 4 (`--backend`).
