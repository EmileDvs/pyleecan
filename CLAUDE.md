# CLAUDE.md

Guide to the pyleecan code base for Claude Code. Keep it up to date while the
migration goes on (see "Keeping this file up to date" at the end).

## Project

Pyleecan (Python Library for Electrical Engineering Computational Analysis):
electrical machine design and simulation (machines, slots, windings, magnetics
with FEMM, forces, losses, structural, optimization, GUI in PySide6).

- Python >= 3.14, managed with `uv` (`uv.lock`), build backend `uv_build`.
- Source in `src/pyleecan/`, tests in `Tests/`, tutorials in `Tutorials/`.
- Branch `switch_to_dataclass`: migration of the classes from the legacy
  CSV-generated classes to dataclass and pydantic classes.
  Roadmap and step checklist: [PLAN.md](PLAN.md). Detailed tasks of the
  remaining steps (review lists, findings): [BACKLOG.md](BACKLOG.md).
  History: [CHANGELOG.md](CHANGELOG.md).
- **Frozen since Step 12 (2026-11-22)**: `Methods_new` (every sub-package,
  `FROZEN_PACKAGES`), the hand-written `Functions_new` modules
  (`HAND_WRITTEN_FUNCTION_MODULES`: `check_parent.py`, `get_logger.py`,
  `FEMM/femm_pyleecan.py`) and `GUI_new` (`GUI_NEW_FROZEN`, except its
  `Gen_*` modules) are edited by hand (Steps 13–17). The class generator
  still builds `Classes_new` / `Classes_pydantic` from `Methods_new`, read
  through the shim `to_legacy_names`: keep the import forms it translates
  (imports of `Classes_new` / `Functions_new`, class loads as local imports).
  After editing `Methods_new`, regenerate the classes.
- The legacy folders change only through merges of upstream pull requests
  (Step 7). Since the freeze, a change merged in the legacy `Methods` or `GUI`
  is ported by hand to `Methods_new` / `GUI_new`; the other `Functions`
  modules are still generated.

## Package layout (`src/pyleecan/`)

| Folder | Role | Edit? |
|---|---|---|
| `Classes/` | Legacy classes, generated from the CSV files in `Generator/ClassesRef/` | Never |
| `Methods/` | Legacy methods, inlined into the legacy classes | Never |
| `Functions/` | Legacy functions | Never |
| `Classes_new/` | Dataclass + dacite backend, generated | Never by hand: change the generator |
| `Classes_pydantic/` | Pydantic v2 backend (reference target), generated | Never by hand: change the generator |
| `Methods_new/` | Methods shared by both backends, written by the method generator from `Methods/` until the freeze | Hand-written since Step 12 (all sub-packages frozen); regenerate the classes after an edit |
| `Functions_new/` | Functions for `Classes_new`, written by the functions generator from `Functions` | Generated, except `HAND_WRITTEN_FUNCTION_MODULES` (hand-written since Step 12) |
| `Functions_pydantic/` | Generated from `Functions_new` by import rewriting | Never by hand |
| `classes_common/` | Backend-agnostic support: class lookup, `ClassInfo`, errors, checks, legacy dump/values, equality, custom setters, parent types | Hand-written (incl. `logger_context.py`: loggers without parents), except `errors.py`, `parent_types.py` and `retrocompatibility.py` (generated) |
| `Generator/` | Legacy generators (`ClassGenerator/*.py`, GUI, UML) and the CSV class definitions (`ClassesRef/`) | Legacy generator: never |
| `Generator/ClassGenerator/New/` | New generators (classes, methods, functions, tests) | Yes: this is where changes go |
| `GUI/`, `Data/`, `Results/` | Legacy GUI, reference machines/materials, outputs | GUI: never (legacy) |
| `GUI_new/`, `GUI_pydantic/` | GUI on the dataclass / pydantic classes, generated from `GUI` (Step 10); `Resources/pyleecan_rc.py` is a shim loading the legacy compiled resources | `GUI_new`: hand-written since Step 12, except the `Gen_*` modules (generated from `ClassInfo`); `GUI_pydantic`: never by hand (import rewriting of `GUI_new`) |

### New class backends

- Sub-packages are snake_case, from the legacy packages: `converter`, `elmer`,
  `geometry`, `gui_option` (legacy `GUI_Option`), `import_data` (legacy
  `Import`), `loss`, `machine`, `material`, `mesh`, `optimization`, `output`,
  `post`, `scidatatool`, `slot`, `simulation`, plus `electrical`, `magnetics`,
  `force`, `structural` taken out of `Simulation`. Same tree in
  `Classes_pydantic/` and `Methods_new/`.
- Module names are snake_case (`geometry/arc_1.py`) and unique across
  sub-packages. Sub-package `__init__.py` files do not import their classes.
- `_package` keeps the legacy package name during Phase 1.
- Bases: target `PyleecanClass` (`Classes_new/_pyleecan_class.py`) /
  `PyleecanModel` (`Classes_pydantic/_pyleecan_model.py`), and the legacy
  layer `LegacyClass` (`_legacy_class.py`) / `LegacyModel` (`_legacy_model.py`)
  that generated root classes inherit in Phase 1. Legacy-only behaviours (None
  everywhere, `-1` default, `as_dict`/`from_dict`/`copy`/`compare`, unknown
  keys ignored on load, parent links) live only in the legacy layer.
- Target API (both backends): `model_dump`, `model_validate`, `model_copy`,
  ndarray-aware `==`. No parent links in the target model.
- Dataclass validation (type/min/max): `Classes_new/_validation.py`.
- `ClassInfo` (`_class_info.py`) is built from the classes, not from CSV/JSON.
- `_smoot/`, `_swat_em/` are vendored; `Classes_pydantic` imports them from
  `Classes_new`.
- Method errors are generated once in `classes_common/errors.py`; classes keep
  an alias attribute (`Segment.PointSegmentError`).

## Generators (`Generator/ClassGenerator/New/`)

| Module | Role |
|---|---|
| `run_generate_classes.py` | Entry point: methods, both class backends, functions, tests |
| `class_generator.py` | Class assembly (fields, inlining, imports, `BACKENDS`, `ROOT_BASES`, sub-packages) |
| `generate_methods_new.py` | Wrote `Methods_new` from legacy `Methods` (modernization pipeline); since the freeze only its `__init__.py` (every package in `FROZEN_PACKAGES`) |
| `modernize.py`, `source_names.py`, `function_module_names.py` | Shared modernization passes and name mappings for methods and functions |
| `type_hints.py` | Type hints from the numpydoc docstrings |
| `legacy_fixes.py` | Fixes of legacy method bugs (`LEGACY_FIXES`), applied to the `Methods_new` copies before modernization |
| `container_arguments.py`, `parent_reads.py` | Step 11: container arguments replacing the parent reads (`CONTAINER_ARGUMENTS`, fallback `classes_common.parents.container_or_parent`); classification report of the parent reads |
| `femm_object.py` | Interface objects gathering the functions of a folder: `femm_pyleecan` (`Functions/FEMM`, with the handler), `gmsh_pyleecan` (`Functions/GMSH`), `pv_plotter_pyleecan` (`Functions/Plot/Pyvista`) (static methods); aliases, callers |
| `moved_functions.py` | Legacy functions moved to a class as methods (`MOVED_FUNCTIONS`), deprecated aliases at the old paths |
| `generate_function_new_classes.py` | `Functions_new` |
| `generate_function_pydantic.py` | `Functions_pydantic` from `Functions_new` |
| `generate_gui_new.py` | `GUI_new` from `GUI` until the freeze (method pipeline, GUI imports redirected); still writes the `Gen_*` widget setup of `GUI_new` (from `ClassInfo` and the `gen_list.json` files) and `GUI_pydantic` from `GUI_new` (imports) |
| `generate_test_new_classes.py` | `Tests/New` tree from the legacy tests |

Full regeneration:

```
uv run python -m pyleecan.Generator.ClassGenerator.New.run_generate_classes
```

Rules: a moved pass must keep the generated classes byte-identical; passes are
idempotent; method sources hold no backend-specific logic.

Parallel run (`worker_pool.py`): one process pool for the whole run (the
work is pure-Python AST passes, threads would be serialized by the GIL). Task
functions must be module-level; the state of a step goes to the workers once
through a pickle file. A script that runs the generators must guard its code
with `if __name__ == "__main__":` (Windows workers re-import the main module).
Ruff is never called per class in a full run: the classes are built as drafts
(`generate_class(..., return_draft=True)`) and finished together
(`advance_class` / `run_ruff_requests`), one Ruff process per step.

Pitfalls:
- The generators delete and rewrite the generated folders: a shell whose
  working directory is inside one (e.g. `Methods_new/slot`) locks it on Windows
  (`PermissionError: [WinError 32]`) and the run stops halfway. Run from the
  repository root.
- `run_generate_classes(class_list=...)` takes CSV file names
  (`["ConvertMC.csv"]`), not class names.
- Type hints: `type_hints.py` drafts them from the numpydoc docstrings; the
  docstrings of the legacy `Methods` cannot be fixed, so incomplete ones are
  completed by `PARAMETER_OVERRIDES` / `RETURN_OVERRIDES`. Check a package
  with `uv run ty check src/pyleecan/Methods_new/<package>`.

## Tests

- `Tests/` holds the legacy suites; `Tests/New/` holds the generated tree for
  the new backends plus generator unit tests (`Tests/New/test_*.py`) and
  cross-backend tests (`Tests/New/Cross`).
- Backend selection: `pytest --backend=dataclass|pydantic` (default
  `dataclass`). Tests import through the alias packages `backend_classes` /
  `backend_functions` (`Tests/New/_backend.py`, `Tests/New/conftest.py`).
- Usual scope: `Tests/Classes` and `Tests/New/Classes`, plus the small tests
  of the generator feature being worked on. Do not run the long legacy-derived
  suites; the older generator tests are run for the final validation only.

```
uv run pytest Tests/New/Classes --backend=pydantic
uv run pytest Tests/Classes
```

- Lint and types: `ruff`, `ty` (for example `uv run ty check src/pyleecan/Methods_new/slot`).

## Conventions

- One commit per increment; `[WiP]` prefix during the migration.
- Each new generator feature gets small unit tests.
- New packages and sub-packages are lowercase (PEP 8).
- Keep the PLAN.md and BACKLOG.md checkboxes and the CHANGELOG up to date:
  details and findings go in BACKLOG.md, PLAN.md stays a short checklist.

## Keeping this file up to date

Update this file when the structure changes: a new package or generator
module, a step of PLAN.md that changes where code lives (for example a frozen
`Methods_new` package, the Phase 2 layout), a new test command or option.
Keep it a map of the code base; the detailed plan stays in PLAN.md.
