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
- **`PyleecanModel`** (pydantic v2) base and generation of the Geometry
  package as pydantic models (work in progress, to be moved to
  `Classes_pydantic`).
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

### Changed

- Generated classes use regular (function-local) imports for known class
  names instead of dynamic imports; `import_class` is kept for names known at
  runtime only (serialized `__class__`).
- `Segment`, `Arc1`, `Arc2` and `Arc3` are built with keyword arguments in
  the new methods and functions.
- Class constants refactored to avoid circular imports; attribute metadata
  (unit, min, max) and descriptions follow the legacy definitions.
- The load function returns objects of the new classes.
- Normalization classes follow the class naming convention (`Norm_ref` ->
  `NormRef`); the legacy names remain accepted when loading files.

### Fixed

- Generation of the phase axis.

### Status

Phase 1 progress (see [PLAN.md](src/pyleecan/Generator/ClassGenerator/New/PLAN.md)):

| Step | Status |
|---|---|
| 0. Separate the implementations in the generator | in progress: class sub-packages done |
| 1. Split the bases (target / legacy layer) | to do |
| 2. Type, min and max validation for dataclasses | to do |
| 3. `Functions_pydantic` | to do |
| 4. Phase 1 test architecture (`--backend`) | to do |
| 5. Package refactor pass (`Methods_new`, no parent links) | to do |
| 6. Remaining utility functions | to do |

Legacy class tests (`Tests/New/Classes`): 2369 passed, 455 failed. The
failures are the type, min and max checks that the dataclasses do not
implement yet (Step 2).
