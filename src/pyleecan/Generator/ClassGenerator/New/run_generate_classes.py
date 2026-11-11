import ast
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os import cpu_count, listdir, remove
from os.path import basename, isdir, isfile, join

from pyleecan.definitions import DOC_DIR, INT_DIR, MAIN_DIR, PACKAGE_NAME
from pyleecan.Functions.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _shared_error_definitions,
    _write_shared_errors,
    class_module_name,
    generate_class,
    get_class_import_graph,
    parent_type_mapping,
    validate_class_module_names,
)
from pyleecan.Generator.read_fct import read_all

EXPERIMENTAL_INIT = '''"""Experimental dataclass-based Pyleecan classes."""

from json import load
from os.path import dirname, join

def get_class_dict():
    """Return the CSV-derived class generation dictionary."""
    path = join(dirname(__file__), "_class_dict.json")
    with open(path, encoding="utf-8") as class_dict_file:
        return load(class_dict_file)
'''

EXPERIMENTAL_IMPORT = '''"""Generated class imports; do not edit by hand."""

from importlib import import_module

from {error_module} import InitUnKnowClassError

_CLASS_MODULES = {class_modules}
_LEGACY_NAMES = {legacy_names}
__all__ = ["import_class", *_CLASS_MODULES]


def import_class(class_name, prop_name=""):
    """Import a generated class by name."""
    class_name = _LEGACY_NAMES.get(class_name, class_name)
    module_name = _CLASS_MODULES.get(class_name)
    if module_name is None:
        message = "Unknow class name " + str(class_name)
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message)
    target = __package__ + "." + module_name
    try:
        module = import_module(target)
    except ModuleNotFoundError as error:
        if error.name != target:
            raise
        message = "Unknow class name " + class_name
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message) from error
    try:
        return getattr(module, class_name)
    except AttributeError as error:
        message = "Unknow class name " + class_name
        if prop_name:
            message += " in init_dict for property " + prop_name
        else:
            message += " when loading"
        raise InitUnKnowClassError(message) from error


def __getattr__(name):
    if name not in _CLASS_MODULES:
        raise AttributeError(f"module {{__name__!r}} has no attribute {{name!r}}")
    value = import_class(name)
    globals()[name] = value
    return value
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
):
    """Generate dataclasses in Classes_new without modifying legacy outputs.

    The initializer, class dictionary, parent mapping, and shared exceptions
    are generated from the full CSV dictionary even during partial generation.
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

    Returns
    -------
    None
    """
    _validate_import_style(import_style)
    CLASS_DIR = join(root_path, "Classes_new")
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

    if not isdir(CLASS_DIR) or not isfile(join(CLASS_DIR, "_pyleecan_class.py")):
        raise FileNotFoundError(
            "Experimental output requires Classes_new/_pyleecan_class.py: "
            + CLASS_DIR
        )
    import_path = join(CLASS_DIR, "_import.py")
    if class_list is not None and isfile(import_path):
        with open(import_path, encoding="utf-8") as import_file:
            previous = ast.parse(import_file.read(), filename=import_path)
        for definition in previous.body:
            if (
                isinstance(definition, ast.FunctionDef)
                and definition.name == "import_class"
                and definition.args.args
                and definition.args.args[0].arg == "mod_name"
            ):
                raise ValueError(
                    "The experimental import_class API changed; perform a full "
                    "generation before generating individual classes."
                )
    class_names = (
        set(basename(csv_path)[:-4] for csv_path in class_list)
        if class_list is not None
        else set(gen_dict)
    )
    generation_names = sorted(name for name in gen_dict if name in class_names)
    shared_errors = _shared_error_definitions(
        gen_dict, CLASS_DIR, soft_name, class_import_graph
    )
    _write_shared_errors(CLASS_DIR, shared_errors)

    if class_list is None:
        # Deleting all the previous class
        print("Deleting old class files...")
        for file_name in listdir(CLASS_DIR):
            if file_name[0] != "_":
                remove(join(CLASS_DIR, file_name))
    _generate_classes(
        gen_dict,
        generation_names,
        CLASS_DIR,
        soft_name,
        class_import_graph,
        max_workers,
        import_style=import_style,
        shared_error_definitions=shared_errors,
    )
    _write_experimental_bookkeeping(CLASS_DIR, gen_dict, soft_name, import_style)


def _write_experimental_bookkeeping(class_dir, gen_dict, soft_name, import_style):
    """Write the experimental package API and full generated metadata."""
    with open(join(class_dir, "__init__.py"), "w", encoding="utf-8") as init_file:
        init_file.write(EXPERIMENTAL_INIT)
    with open(join(class_dir, "_class_dict.json"), "w", encoding="utf-8") as json_file:
        json.dump(gen_dict, json_file, sort_keys=True, indent=4, separators=(",", ": "))
    _write_parent_types(class_dir, gen_dict)
    class_modules = {
        NORMALIZATION_CLASS_NAMES.get(name, name): class_module_name(name)
        for name in sorted(gen_dict)
    }
    legacy_names = {
        name: NORMALIZATION_CLASS_NAMES[name]
        for name in sorted(gen_dict) if name in NORMALIZATION_CLASS_NAMES
    }
    error_module = "._error" if import_style == "relative" else (
        soft_name + ".Classes_new._error"
    )
    with open(join(class_dir, "_import.py"), "w", encoding="utf-8") as import_file:
        import_file.write(
            EXPERIMENTAL_IMPORT.format(
                error_module=error_module,
                class_modules=repr(class_modules),
                legacy_names=repr(legacy_names),
            )
        )


def _write_parent_types(class_dir, gen_dict):
    """Write parent rules for all generated classes."""
    mapping = parent_type_mapping(gen_dict)
    with open(
        join(class_dir, "_parent_types.py"), "w", encoding="utf-8"
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


def _generate_classes(
    gen_dict,
    generation_names,
    class_dir,
    soft_name,
    class_import_graph,
    max_workers,
    import_style="absolute",
    shared_error_definitions=None,
):
    def generate_one_class(class_name, import_graph=None):
        print("Generation of " + class_name + " class")
        generation_kwargs = {
            "soft_name": soft_name,
            "import_style": import_style,
            "shared_error_definitions": shared_error_definitions,
        }
        if import_graph is not None:
            generation_kwargs["class_import_graph"] = import_graph
        generate_class(gen_dict, class_name, class_dir, **generation_kwargs)

    if generation_names and len(class_import_graph) == len(gen_dict):
        if max_workers is None:
            max_workers = min(8, cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(
                    generate_one_class,
                    class_name,
                    class_import_graph,
                )
                for class_name in generation_names
            ]
            for future in futures:
                future.result()
    else:
        # Preserve the generator's dynamic cycle checks when no complete snapshot exists.
        for class_name in generation_names:
            generate_one_class(class_name)


def run_generate_classes(
    doc_dir=DOC_DIR,
    int_dir=INT_DIR,
    main_dir=MAIN_DIR,
    soft_name=PACKAGE_NAME,
    class_list=None,
    max_workers=None,
    import_style="absolute",
):
    """Generate experimental dataclasses.

    Experimental generation writes only selected modules in ``Classes_new``
    with snake_case names and does not rewrite CSVs or legacy bookkeeping.
    It also writes an initializer, a full CSV-derived ``_class_dict.json``,
    the full ``_parent_types.py`` mapping, and shared ``_error.py`` definitions,
    even for partial generation. Existing classes need a full regeneration to
    use the shared exceptions.
    Class dictionary keys and metadata retain their source CSV class names.
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
    )

    now = datetime.now()
    print("End at: ", now.strftime("%H:%M:%S"))


if __name__ == "__main__":
    # To generate all classes
    run_generate_classes(max_workers=cpu_count(), import_style="relative")

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

    # list_csv = ["SolutionData.csv", "LUTdq.csv", "OutElec.csv", "OutMag.csv"]

    # To generate only one class
    # run_generate_classes(class_list=list_csv)
