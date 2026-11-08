import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os import cpu_count, listdir, remove
from os.path import basename, isdir, isfile, join, realpath

from pyleecan.definitions import DOC_DIR, INT_DIR, MAIN_DIR, PACKAGE_NAME
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _shared_error_definitions,
    _write_shared_errors,
    generate_class,
    get_class_import_graph,
    parent_type_mapping,
    validate_class_module_names,
)
from pyleecan.Generator.read_fct import read_all
from pyleecan.Generator.write_fct import write_file

# List of the main packages (to sort the classes)
PACKAGE_LIST = ["Geometry", "Machine", "Material", "Slot", "Import"]

EXPERIMENTAL_INIT = '''"""Experimental dataclass-based Pyleecan classes."""

from json import load
from os.path import dirname, join

def get_class_dict():
    """Return the CSV-derived class generation dictionary."""
    path = join(dirname(__file__), "_class_dict.json")
    with open(path, encoding="utf-8") as class_dict_file:
        return load(class_dict_file)
'''


def _validate_import_style(import_style):
    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")


def generate_code(
    root_path,
    gen_dict=None,
    soft_name="pyleecan",
    is_log=True,
    class_list=None,
    max_workers=None,
    is_new=True,
    import_style="absolute",
):
    """Generate the package Classes code according to doc in root_path

    Parameters
    ----------
    root_path : str
        Path to the main folder of the package
    gen_dict : dict
        Generation dictionary (contains all the csv data)
    soft_name : str
        Name of the software to generate
    is_log : bool
        True to add the log related code (get_logger...)
    class_list : list
        List of class csv path to generate
    max_workers : int, optional
        Maximum number of classes to generate concurrently. Defaults to at most 8.
    is_new : bool, optional
        Generate experimental dataclasses in Classes_new without modifying
        legacy class files or bookkeeping. Module names use snake_case without
        the former "_new" suffix. Generate the experimental package initializer,
        the full CSV-derived _class_dict.json, and the parent type mapping, even
        for a partial run. Shared exception classes are generated in _error.py
        from the full generation dictionary, including for partial runs.
        Defaults to True; False selects this generator's legacy output mode.
    import_style : str, optional
        "relative" or "absolute" imports from the generated package in class files.

    Returns
    -------
    None
    """
    _validate_import_style(import_style)
    CLASS_DIR = join(root_path, "Classes_new" if is_new else "Classes")
    FUNC_DIR = join(root_path, "Functions")
    DOC_DIR = join(root_path, "Generator", "ClassesRef")
    print("Reading classes csv in: " + DOC_DIR)
    print("Saving generated files in: " + CLASS_DIR)

    # Read all the csv files and snapshot imports before generated files are removed.
    if gen_dict is None:
        gen_dict = read_all(DOC_DIR, soft_name=soft_name)
    if is_new:
        validate_class_module_names(gen_dict)
    class_import_graph = get_class_import_graph(
        join(root_path, "Classes"), gen_dict, soft_name
    )

    if is_new:
        if not isdir(CLASS_DIR) or not isfile(join(CLASS_DIR, "_pyleecan_class.py")):
            raise FileNotFoundError(
                "Experimental output requires Classes_new/_pyleecan_class.py: "
                + CLASS_DIR
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
    else:
        generation_names = None

    if class_list is None:
        # Deleting all the previous class
        print("Deleting old class files...")
        for file_name in listdir(CLASS_DIR):
            if file_name[0] != "_":
                remove(join(CLASS_DIR, file_name))
    else:
        # Deleting only given classes in class_list
        class_name_list = list()
        for csv_path in class_list:
            class_name = basename(csv_path)[:-4]
            class_name_list.append(class_name)
            class_path_py = realpath(join(CLASS_DIR, class_name + ".py"))
            if isfile(class_path_py):
                print("Deleting python class file: " + class_path_py)
                remove(class_path_py)

    if is_new:
        _generate_classes(
            gen_dict,
            generation_names,
            CLASS_DIR,
            soft_name,
            is_log,
            class_import_graph,
            max_workers,
            is_new=True,
            import_style=import_style,
            shared_error_definitions=shared_errors,
        )
        _write_experimental_bookkeeping(CLASS_DIR, gen_dict)
        return

    # A file to import every classes quickly
    import_file = open(join(CLASS_DIR, "_import_all.py"), "w")
    # import_file.write("# -*- coding: utf-8 -*-\n\n")
    import_file.write('"""File generated by generate_code() - \n')
    import_file.write('WARNING! All changes made in this file will be lost!\n"""\n\n')

    # A file to select the constructor according to a string
    load_file = open(join(FUNC_DIR, "load_switch.py"), "w")
    # load_file.write("# -*- coding: utf-8 -*-\n")
    load_file.write('"""File generated by generate_code() - \n')
    load_file.write('WARNING! All changes made in this file will be lost!\n"""\n\n')

    load_file.write("from ..Classes._import_all import *\n\n")
    load_file.write("load_switch = {\n")

    # Keep generated bookkeeping deterministic while class modules are generated in parallel.
    generation_names = []
    for class_name, _ in iter(sorted(list(gen_dict.items()))):
        import_file.write(
            "from ..Classes." + class_name + " import " + class_name + "\n"
        )
        load_file.write('    "' + class_name + '": ' + class_name + ",\n")
        if class_list is None or class_name in class_name_list:
            generation_names.append(class_name)

    import_file.close()
    load_file.write("}\n")
    load_file.close()

    print("Generation of load_switch.py")
    print("Generation of import_all.py")

    _generate_classes(
        gen_dict,
        generation_names,
        CLASS_DIR,
        soft_name,
        is_log,
        class_import_graph,
        max_workers,
        import_style=import_style,
    )

    # Save gen_dict
    class_dict_file = join(CLASS_DIR, "Class_Dict.json")
    with open(class_dict_file, "w") as json_file:
        json.dump(gen_dict, json_file, sort_keys=True, indent=4, separators=(",", ": "))


def _write_experimental_bookkeeping(class_dir, gen_dict):
    """Write the experimental package API and full generated metadata."""
    with open(join(class_dir, "__init__.py"), "w", encoding="utf-8") as init_file:
        init_file.write(EXPERIMENTAL_INIT)
    with open(join(class_dir, "_class_dict.json"), "w", encoding="utf-8") as json_file:
        json.dump(gen_dict, json_file, sort_keys=True, indent=4, separators=(",", ": "))
    _write_parent_types(class_dir, gen_dict)


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
    is_log,
    class_import_graph,
    max_workers,
    is_new=False,
    import_style="absolute",
    shared_error_definitions=None,
):
    def generate_one_class(class_name, import_graph=None):
        print("Generation of " + class_name + " class")
        generation_kwargs = {
            "soft_name": soft_name,
            "is_log": is_log,
            "is_new": is_new,
            "import_style": import_style,
        }
        if import_graph is not None:
            generation_kwargs["class_import_graph"] = import_graph
        if is_new:
            generation_kwargs["shared_error_definitions"] = shared_error_definitions
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
    is_ruff=True,
    soft_name=PACKAGE_NAME,
    is_log=True,
    class_list=None,
    max_workers=None,
    is_new=True,
    import_style="absolute",
):
    """Generate experimental dataclasses by default, or select legacy output.

    Experimental generation writes only selected modules in ``Classes_new``
    with snake_case names and does not rewrite CSVs or legacy bookkeeping.
    It also writes an initializer, a full CSV-derived ``_class_dict.json``,
    the full ``_parent_types.py`` mapping, and shared ``_error.py`` definitions,
    even for partial generation. Existing classes need a full regeneration to
    use the shared exceptions.
    Class dictionary keys and metadata retain their source CSV class names.
    The experimental normalization classes use names such as ``NormVector``;
    their legacy names remain accepted when loading serialized data.
    ``is_ruff`` controls
    full-file formatting of generated legacy modules; dataclasses are always
    formatted by the class generator. ``import_style`` selects "absolute"
    (the default) or "relative" imports in generated class files.
    """

    _validate_import_style(import_style)
    gen_dict = read_all(
        doc_dir, is_internal=False, in_path=int_dir, soft_name=soft_name
    )

    if not is_new:
        for class_dict in gen_dict.values():
            # Write class into csv format following latest template
            write_file(class_dict)

        gen_dict = read_all(
            doc_dir, is_internal=False, in_path=int_dir, soft_name=soft_name
        )

    generate_code(
        main_dir,
        gen_dict,
        soft_name=soft_name,
        is_log=is_log,
        class_list=class_list,
        max_workers=max_workers,
        is_new=is_new,
        import_style=import_style,
    )

    if is_ruff and not is_new:
        selected = (
            set(basename(csv_path)[:-4] for csv_path in class_list)
            if class_list is not None
            else set(gen_dict)
        )
        class_paths = [
            join(main_dir, "Classes", name + ".py")
            for name in sorted(gen_dict)
            if name in selected
        ]
        if class_paths:
            subprocess.run(["ruff", "format", *class_paths], check=True)
    now = datetime.now()
    print("End at: ", now.strftime("%H:%M:%S"))


if __name__ == "__main__":
    # To generate all classes
    run_generate_classes(max_workers=cpu_count(), is_new=True, import_style="relative")

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
