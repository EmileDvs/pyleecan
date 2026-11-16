import json
import warnings
from datetime import datetime
from os import cpu_count, listdir, makedirs, remove
from os.path import basename, isdir, isfile, join
from shutil import rmtree

from pyleecan.definitions import DOC_DIR, INT_DIR, MAIN_DIR, PACKAGE_NAME
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    RUFF_REQUEST_ORDER,
    _prepare_methods_of,
    _shared_error_definitions,
    _write_shared_errors,
    advance_class,
    backend_package,
    class_request,
    class_state,
    class_steps,
    class_subpackage,
    common_dir,
    format_generated_files,
    generate_class,
    get_class_import_graph,
    parent_type_mapping,
    run_class_steps,
    run_ruff_requests,
    validate_class_module_names,
)
from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
    generate_functions,
)
from pyleecan.Generator.ClassGenerator.New.generate_function_pydantic import (
    generate_functions_pydantic,
)
from pyleecan.Generator.ClassGenerator.New.generate_methods_new import (
    generate_methods,
)
from pyleecan.Generator.ClassGenerator.New.generate_test_new_classes import (
    generate_tests,
)
from pyleecan.Generator.ClassGenerator.New.worker_pool import (
    run_tasks,
    shutdown_pool,
    worker_count,
)
from pyleecan.Generator.read_fct import read_all

PACKAGE_INIT = '''"""Experimental Pyleecan classes based on {kind}.

Use ``{package}._class_info.ClassInfo().get_dict()`` to get the class
information (built from the classes themselves).
"""
'''

PACKAGE_INIT_KINDS = {
    "dataclass": "stdlib dataclasses (+ dacite)",
    "pydantic": "pydantic models",
}

BACKEND_SUPPORT_MODULES = {
    "dataclass": (
        "_pyleecan_class.py",
        "_legacy_class.py",
        "_import.py",
        "_class_info.py",
    ),
    "pydantic": (
        "_pyleecan_model.py",
        "_legacy_model.py",
        "_import.py",
        "_class_info.py",
    ),
}
"""Hand-written support modules required in the class package of a backend"""

SUBPACKAGE_INIT = '''"""Generated classes of the {subpackage} sub-package.

Import a class from its module: this file does not import the classes, to
avoid import cycles.
"""
'''


def _validate_import_style(import_style):
    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")


def generate_code(
    root_path,
    gen_dict=None,
    soft_name="pyleecan",
    class_list=None,
    max_workers=None,
    import_style="absolute",
    backend="dataclass",
    prepared_methods=None,
):
    """Generate the classes of a backend without modifying legacy outputs.

    backend "dataclass" writes Classes_new, "pydantic" writes Classes_pydantic.

    The initializer, class dictionary, parent mapping, and shared exceptions
    are generated from the full CSV dictionary and legacy Functions tree even
    during partial generation.
    A full run is required when upgrading from the old two-argument import
    helper. Generate Functions_new before importing the generated classes.
    Class-valued fields with an empty CSV default construct the declared class;
    explicitly supplied None is preserved and -1 constructs the class.

    Parameters
    ----------
    root_path : str
        Path to the main folder of the package
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    soft_name : str
        Name of the software to generate
    class_list : list
        List of class csv path to generate
    max_workers : int, optional
        Maximum number of classes to generate concurrently. Defaults to at most 8.
    import_style : str, optional
        "relative" or "absolute" imports from the generated package in class files.
    backend : str, optional
        "dataclass" (Classes_new) or "pydantic" (Classes_pydantic)
    prepared_methods : dict, optional
        Prepared class methods, shared by the generations of a run (both
        backends): filled by the first generation, reused by the next ones
        (see class_generator._shared_error_definitions). Only valid while the
        method sources (Methods_new, Methods) are unchanged.

    Returns
    -------
    None
    """
    _validate_import_style(import_style)
    package = backend_package(backend)
    CLASS_DIR = join(root_path, package)
    DOC_DIR = join(root_path, "Generator", "ClassesRef")
    print("Reading classes csv in: " + DOC_DIR)
    print("Saving generated files in: " + CLASS_DIR)

    # Read all the csv files and snapshot imports before generated files are removed.
    if gen_dict is None:
        gen_dict = read_all(DOC_DIR, soft_name=soft_name)
    validate_class_module_names(gen_dict)
    class_import_graph = get_class_import_graph(
        join(root_path, "Classes"), gen_dict, soft_name
    )

    for support_module in BACKEND_SUPPORT_MODULES[backend]:
        # Hand-written support modules (not generated)
        if not isdir(CLASS_DIR) or not isfile(join(CLASS_DIR, support_module)):
            raise FileNotFoundError(
                f"Experimental output requires {package}/{support_module}: "
                + CLASS_DIR
            )
    for support_module in (
        "class_lookup.py",
        "class_info.py",
        "check.py",
        "base.py",
        "equality.py",
        "parents.py",
    ):
        # Hand-written shared support (classes_common)
        if not isfile(join(common_dir(CLASS_DIR), support_module)):
            raise FileNotFoundError(
                f"Experimental output requires classes_common/{support_module}"
            )
    class_names = (
        set(basename(csv_path)[:-4] for csv_path in class_list)
        if class_list is not None
        else set(gen_dict)
    )
    generation_names = sorted(name for name in gen_dict if name in class_names)
    if prepared_methods is None:
        prepared_methods = {}  # Shared by the error search and the generation
    if len(class_import_graph) == len(gen_dict):
        # The methods of all the classes are prepared in parallel (the error
        # search then reads them from prepared_methods)
        _prepare_all_methods(
            gen_dict,
            prepared_methods,
            max_workers,
            {
                "gen_dict": gen_dict,
                "class_dir": CLASS_DIR,
                "soft_name": soft_name,
                "class_import_graph": class_import_graph,
            },
        )
    shared_errors = _shared_error_definitions(
        gen_dict, CLASS_DIR, soft_name, class_import_graph, prepared_methods
    )
    _write_shared_errors(CLASS_DIR, shared_errors)

    if class_list is None:
        # Deleting all the previous class modules and sub-packages
        # (the names starting with "_" are support modules or vendored code)
        print("Deleting old class files...")
        for file_name in listdir(CLASS_DIR):
            if file_name[0] != "_":
                path = join(CLASS_DIR, file_name)
                if isdir(path):
                    rmtree(path)
                else:
                    remove(path)
    _write_subpackages(CLASS_DIR, gen_dict, generation_names)
    _generate_classes(
        gen_dict,
        generation_names,
        CLASS_DIR,
        soft_name,
        class_import_graph,
        max_workers,
        import_style=import_style,
        shared_error_definitions=shared_errors,
        backend=backend,
        prepared_methods=prepared_methods,
    )
    _write_experimental_bookkeeping(CLASS_DIR, gen_dict, backend)


def _write_subpackages(class_dir, gen_dict, generation_names):
    """Create the sub-packages of the generated classes (before the threads)."""
    for subpackage in sorted(
        {class_subpackage(name, gen_dict) for name in generation_names}
    ):
        makedirs(join(class_dir, subpackage), exist_ok=True)
        with open(
            join(class_dir, subpackage, "__init__.py"), "w", encoding="utf-8"
        ) as init_file:
            init_file.write(SUBPACKAGE_INIT.format(subpackage=subpackage))


def _write_experimental_bookkeeping(class_dir, gen_dict, backend):
    """Write the experimental package API and full generated metadata."""
    with open(join(class_dir, "__init__.py"), "w", encoding="utf-8") as init_file:
        init_file.write(
            PACKAGE_INIT.format(
                kind=PACKAGE_INIT_KINDS[backend], package=backend_package(backend)
            )
        )
    _write_parent_types(class_dir, gen_dict)
    # _import.py is hand-written: the module of a class is derived from its
    # name (class_module_name), no generated class table is needed


def _write_parent_types(class_dir, gen_dict):
    """Write parent rules for all generated classes."""
    mapping = parent_type_mapping(gen_dict)
    with open(
        join(common_dir(class_dir), "parent_types.py"), "w", encoding="utf-8"
    ) as parent_file:
        parent_file.write('"""Generated parent type rules; do not edit by hand."""\n\n')
        parent_file.write("PARENT_TYPES = {\n")
        for (module, name), parents in sorted(mapping.items()):
            key = f"({json.dumps(module)}, {json.dumps(name)})"
            items = [
                f"({json.dumps(parent_module)}, {json.dumps(parent_name)})"
                for parent_module, parent_name in parents
            ]
            if len(items) == 1 and len(key) + len(items[0]) + 11 <= 88:
                parent_file.write(f"    {key}: ({items[0]},),\n")
            else:
                parent_file.write(f"    {key}: (\n")
                parent_file.writelines(f"        {item},\n" for item in items)
                parent_file.write("    ),\n")
        parent_file.write("}\n")


def _prepare_class_task(state, class_name):
    """Prepare the methods of a class (worker task).

    Returns
    -------
    result : tuple
        (class name, prepared methods, [(warning message, category)])
    """
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        prepared = _prepare_methods_of(
            state["gen_dict"],
            state["class_dir"],
            class_name,
            state["soft_name"],
            state["class_import_graph"],
        )
    return (
        class_name,
        prepared,
        [(str(item.message), item.category) for item in recorded],
    )


def _build_drafts_task(state, class_names, prepared_entries):
    """Build the drafts of a chunk of classes (worker task).

    A draft is a class before the Ruff steps of the end of its generation
    (class_generator.ClassDraft): the drafts of all the classes are finished
    together by run_class_steps, with one Ruff process per step for all of
    them (process creation is slow on Windows and Ruff is starved by busy
    workers: per-class Ruff calls do not scale).

    Returns
    -------
    drafts : list
        ClassDraft of each class
    """
    kwargs = {}
    if state["class_import_graph"] is not None:
        kwargs["class_import_graph"] = state["class_import_graph"]
    drafts = []
    for class_name, prepared_entry in zip(class_names, prepared_entries, strict=True):
        print("Generation of " + class_name + " class", flush=True)
        drafts.append(
            generate_class(
                state["gen_dict"],
                class_name,
                state["class_dir"],
                soft_name=state["soft_name"],
                import_style=state["import_style"],
                shared_error_definitions=state["shared_error_definitions"],
                backend=state["backend"],
                prepared_methods=(
                    {class_name: prepared_entry} if prepared_entry is not None else None
                ),
                format_output=False,
                return_draft=True,
                **kwargs,
            )
        )
    return drafts


def _advance_classes_task(state, class_states, outputs):
    """Advance classes with the outputs of their Ruff requests (worker task)."""
    return [
        advance_class(class_state_, output, state["gen_dict"])
        for class_state_, output in zip(class_states, outputs, strict=True)
    ]


def _finish_drafts(drafts, gen_dict, max_workers):
    """Finish the class drafts (class_generator.advance_class).

    The Ruff requests of the classes run together, one Ruff process per
    request kind for all the classes; the steps between them run in the
    workers.

    Returns
    -------
    paths : list
        Paths of the generated modules
    """
    pending = [class_state(draft) for draft in drafts]
    paths = []
    state = {"gen_dict": gen_dict}
    while pending:
        kind = min(
            (class_request(item)[0] for item in pending), key=RUFF_REQUEST_ORDER.index
        )
        batch = [item for item in pending if class_request(item)[0] == kind]
        pending = [item for item in pending if class_request(item)[0] != kind]
        outputs = run_ruff_requests(kind, [class_request(item)[1:] for item in batch])
        size = -(-len(batch) // worker_count(max_workers, len(batch)))
        results = run_tasks(
            _advance_classes_task,
            state,
            [
                (batch[start : start + size], outputs[start : start + size])
                for start in range(0, len(batch), size)
            ],
            max_workers,
        )
        for result in (item for chunk in results for item in chunk):
            if isinstance(result, str):
                paths.append(result)
            else:
                pending.append(result)
    return paths


CHUNKS_PER_WORKER = 3
"""Chunks of classes per worker: more chunks balance the load, fewer chunks
start fewer Ruff processes"""


def _class_chunks(gen_dict, class_names, workers):
    """Chunks of classes, the largest classes (methods) spread over them."""
    count = max(1, min(len(class_names), workers * CHUNKS_PER_WORKER))
    ordered = sorted(
        class_names, key=lambda name: (-len(gen_dict[name]["methods"]), name)
    )
    chunks = [[] for _ in range(count)]
    for index, name in enumerate(ordered):
        cycle, position = divmod(index, count)
        # Back and forth: each chunk gets large and small classes
        chunks[position if cycle % 2 == 0 else count - 1 - position].append(name)
    return [sorted(chunk) for chunk in chunks if chunk]


def _prepare_all_methods(gen_dict, prepared_methods, max_workers, state):
    """Prepare (in parallel) the methods of the classes missing in
    prepared_methods; the warnings other than the inline fallbacks are
    reported here, the inline fallbacks by the class generation."""
    missing = [
        name
        for name, info in sorted(gen_dict.items())
        if info.get("methods") and name not in prepared_methods
    ]
    results = run_tasks(
        _prepare_class_task, state, [(name,) for name in missing], max_workers
    )
    for name, prepared, recorded in results:
        prepared_methods[name] = (prepared, recorded)
        for message, category in recorded:
            if not message.startswith("Could not inline "):
                warnings.warn(message, category, stacklevel=2)


def _generate_classes(
    gen_dict,
    generation_names,
    class_dir,
    soft_name,
    class_import_graph,
    max_workers,
    import_style="absolute",
    shared_error_definitions=None,
    backend="dataclass",
    prepared_methods=None,
):
    """Generate the classes (in parallel, worker_pool), then format them."""
    prepared_methods = prepared_methods if prepared_methods is not None else {}
    complete_graph = len(class_import_graph) == len(gen_dict)
    state = {
        "gen_dict": gen_dict,
        "class_dir": class_dir,
        "soft_name": soft_name,
        # Without a complete snapshot, the generator's dynamic cycle checks
        # (one class after the other)
        "class_import_graph": class_import_graph if complete_graph else None,
        "import_style": import_style,
        "backend": backend,
        "shared_error_definitions": shared_error_definitions,
    }
    chunks = _class_chunks(
        gen_dict, generation_names, worker_count(max_workers, len(generation_names))
    )
    if not complete_graph:
        # Dynamic cycle checks: the classes are written one after the other
        paths = []
        for name in generation_names:
            draft = _build_drafts_task(state, [name], [prepared_methods.get(name)])[0]
            paths.extend(run_class_steps([class_steps(draft, gen_dict)]))
        format_generated_files(paths)
        return
    results = run_tasks(
        _build_drafts_task,
        state,
        [(chunk, [prepared_methods.get(name) for name in chunk]) for chunk in chunks],
        max_workers,
    )
    drafts = [draft for chunk_drafts in results for draft in chunk_drafts]
    paths = _finish_drafts(drafts, gen_dict, max_workers)
    format_generated_files(paths)


def run_generate_classes(
    doc_dir=DOC_DIR,
    int_dir=INT_DIR,
    main_dir=MAIN_DIR,
    soft_name=PACKAGE_NAME,
    class_list=None,
    max_workers=None,
    import_style="absolute",
    backend="dataclass",
    prepared_methods=None,
):
    """Generate the experimental classes of a backend.

    backend "dataclass" writes ``Classes_new``, "pydantic" writes
    ``Classes_pydantic`` (see class_generator.BACKENDS).

    Experimental generation writes only selected modules in ``Classes_new``
    with snake_case names and does not rewrite CSVs or legacy bookkeeping.
    It also writes an initializer, the full ``classes_common/parent_types.py``
    mapping and shared ``classes_common/errors.py`` definitions, even for
    partial generation. Existing
    classes need a full regeneration to use the shared exceptions.
    The class information is no longer written: it is rebuilt from the
    dataclasses by ``Classes_new._class_info.ClassInfo``.
    The experimental normalization classes use names such as ``NormVector``;
    their legacy names remain accepted when loading serialized data.
    Dataclasses are formatted by the class generator. ``import_style`` selects "absolute"
    (the default) or "relative" imports in generated class files.
    """

    _validate_import_style(import_style)
    gen_dict = read_all(
        doc_dir, is_internal=False, in_path=int_dir, soft_name=soft_name
    )

    generate_code(
        main_dir,
        gen_dict,
        soft_name=soft_name,
        class_list=class_list,
        max_workers=max_workers,
        import_style=import_style,
        backend=backend,
        prepared_methods=prepared_methods,
    )

    now = datetime.now()
    print("End at: ", now.strftime("%H:%M:%S"))


if __name__ == "__main__":
    # Methods_new from the legacy Methods (read by the class generator)
    generate_methods()

    # To generate all classes, for each backend (the class methods are
    # prepared once, for both backends)
    prepared_methods = {}
    for backend in ("dataclass", "pydantic"):
        run_generate_classes(
            max_workers=cpu_count(),
            import_style="relative",
            backend=backend,
            prepared_methods=prepared_methods,
        )

    generate_functions()
    generate_functions_pydantic()  # From Functions_new

    generate_tests()
    shutdown_pool()  # Workers of the class generation

    # list_csv = [
    #     "Data.csv",
    #     "Data1D.csv",
    #     "DataDual.csv",
    #     "DataFreq.csv",
    #     "DataLinspace.csv",
    #     "DataND.csv",
    #     "DataPattern.csv",
    #     "DataTime.csv",
    #     "Norm_affine.csv",
    #     "Norm_func.csv",
    #     "Norm_indices.csv",
    #     "Norm_ref.csv",
    #     "Norm_vector.csv",
    #     "Normalization.csv",
    #     "RequestedAxis.csv",
    #     "VectorField.csv",
    # ]

    # list_csv = ["Section.csv"]

    # # To generate only one class
    # run_generate_classes(class_list=list_csv, import_style="relative")
