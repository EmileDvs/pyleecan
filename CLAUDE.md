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
  Roadmap and progress checklist: [PLAN.md](PLAN.md). History: [CHANGELOG.md](CHANGELOG.md).

## Package layout (`src/pyleecan/`)

| Folder | Role | Edit? |
|---|---|---|
| `Classes/` | Legacy classes, generated from the CSV files in `Generator/ClassesRef/` | Never |
| `Methods/` | Legacy methods, inlined into the legacy classes | Never |
| `Functions/` | Legacy functions | Never |
| `Classes_new/` | Dataclass + dacite backend, generated | Never by hand: change the generator |
| `Classes_pydantic/` | Pydantic v2 backend (reference target), generated | Never by hand: change the generator |
| `Methods_new/` | Methods shared by both backends, written by the method generator from `Methods/` | Generated, except frozen (hand-written) packages |
| `Functions_new/` | Functions for `Classes_new`, bootstrapped one legacy package at a time | Bootstrapped modules are hand-written |
| `Functions_pydantic/` | Generated from `Functions_new` by import rewriting | Never by hand |
| `classes_common/` | Backend-agnostic support: class lookup, `ClassInfo`, errors, checks, legacy dump/values, equality, custom setters, parent types | Hand-written, except `errors.py` and `parent_types.py` (generated) |
| `Generator/` | Legacy generators (`ClassGenerator/*.py`, GUI, UML) and the CSV class definitions (`ClassesRef/`) | Legacy generator: never |
| `Generator/ClassGenerator/New/` | New generators (classes, methods, functions, tests) | Yes: this is where changes go |
| `GUI/`, `Data/`, `Results/` | GUI, reference machines/materials, outputs | |

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
| `generate_methods_new.py` | Writes `Methods_new` from legacy `Methods` (modernization pipeline) |
| `modernize.py`, `source_names.py`, `function_module_names.py` | Shared modernization passes and name mappings for methods and functions |
| `type_hints.py` | Type hints from the numpydoc docstrings |
| `generate_function_new_classes.py` | `Functions_new` |
| `generate_function_pydantic.py` | `Functions_pydantic` from `Functions_new` |
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
- Keep the PLAN.md checkboxes and the CHANGELOG up to date.

## Keeping this file up to date

Update this file when the structure changes: a new package or generator
module, a step of PLAN.md that changes where code lives (for example a frozen
`Methods_new` package, the Phase 2 layout), a new test command or option.
Keep it a map of the code base; the detailed plan stays in PLAN.md.
