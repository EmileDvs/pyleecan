"""Backend comparison (PLAN.md Step 18): micro benchmarks of the class
implementations on the same scenarios.

Not a test module (not collected by pytest). Run from the repository root:

    MPLBACKEND=Agg uv run python -m Tests.New.Benchmark.benchmark_backends

Each backend is timed in its own subprocess (no shared import cache):
``legacy`` (the CSV-generated classes, reference), ``dataclass``
(``Classes_new`` + dacite) and ``pydantic`` (``Classes_pydantic``). The
result is a Markdown table on stdout (median of the repeats, in
microseconds per call unless stated).
"""

import json
import statistics
import subprocess
import sys
import timeit

BACKENDS = {
    "legacy": ("pyleecan.Classes", "pyleecan.Functions.load"),
    "dataclass": ("pyleecan.Classes_new", "pyleecan.Functions_new.load"),
    "pydantic": ("pyleecan.Classes_pydantic", "pyleecan.Functions_pydantic.load"),
}
MACHINES = ("Toyota_Prius", "IPMSM_B", "SCIM_006", "SPMSM_001", "Railway_Traction")
REPEAT = 5


def _time(stmt, number, repeat=REPEAT):
    """Median time of one call [us]."""
    times = timeit.repeat(stmt, number=number, repeat=repeat)
    return statistics.median(times) / number * 1e6


def run_backend(name):
    """Timings of one backend (run in its own process)."""
    import importlib
    import time
    from os.path import join

    from pyleecan.definitions import DATA_DIR

    t0 = time.perf_counter()
    package, load_module = BACKENDS[name]
    load = importlib.import_module(load_module).load
    if name == "legacy":
        Segment = importlib.import_module(package + ".Segment").Segment
        LamSlotWind = importlib.import_module(package + ".LamSlotWind").LamSlotWind
    else:
        Segment = importlib.import_module(package + ".geometry.segment").Segment
        LamSlotWind = importlib.import_module(
            package + ".machine.lam_slot_wind"
        ).LamSlotWind
    results = {"import [ms]": (time.perf_counter() - t0) * 1e3}

    results["Segment()"] = _time(lambda: Segment(begin=0, end=1j), 2000)
    results["LamSlotWind()"] = _time(lambda: LamSlotWind(), 200)
    seg = Segment(begin=0, end=1j)

    def assign_valid():
        seg.begin = 1 + 1j

    results["valid assignment"] = _time(assign_valid, 20000)
    lam = LamSlotWind()

    def assign_invalid():
        try:
            lam.Rint = -1.0  # below the minimum
        except Exception:
            pass

    results["invalid assignment"] = _time(assign_invalid, 2000)

    machines = {}
    for machine_name in MACHINES:
        path = join(DATA_DIR, "Machine", machine_name + ".json")
        t0 = time.perf_counter()
        machines[machine_name] = load(path)
        results[f"load {machine_name} [ms]"] = (time.perf_counter() - t0) * 1e3
    prius = machines["Toyota_Prius"]
    if name == "legacy":
        dump = lambda: prius.as_dict()  # noqa: E731
        data = prius.as_dict()
        validate = lambda: type(prius)(init_dict=data)  # noqa: E731
        copy = lambda: prius.copy()  # noqa: E731
    else:
        dump = lambda: prius.model_dump()  # noqa: E731
        data = prius.model_dump()
        validate = lambda: type(prius).model_validate(data)  # noqa: E731
        copy = lambda: prius.model_copy(deep=True)  # noqa: E731
    results["dump Prius"] = _time(dump, 20)
    results["validate Prius"] = _time(validate, 20)
    results["copy Prius"] = _time(copy, 20)
    other = copy()
    results["== Prius"] = _time(lambda: prius == other, 20)
    results["comp_surface (stator slot)"] = _time(
        lambda: prius.stator.slot.comp_surface(), 200
    )
    return results


def run_files(name):
    """Load and save of every machine file of Data/Machine, memory (run in its
    own process): total times [ms], peak memory of the loaded machines [MB]."""
    import importlib
    import tempfile
    import time
    import tracemalloc
    from os import listdir
    from os.path import join

    from pyleecan.definitions import DATA_DIR

    load = importlib.import_module(BACKENDS[name][1]).load
    folder = join(DATA_DIR, "Machine")
    files = sorted(f for f in listdir(folder) if f.endswith(".json"))
    load(join(folder, files[0]))  # Class imports out of the timing
    tracemalloc.start()
    t0 = time.perf_counter()
    machines = {}
    failed = []
    for file_name in files:
        try:
            machines[file_name] = load(join(folder, file_name))
        except Exception as error:  # Reported, not timed again
            failed.append(f"{file_name}: {type(error).__name__}")
    load_time = (time.perf_counter() - t0) * 1e3
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.perf_counter()
        for file_name, machine in machines.items():
            try:
                machine.save(join(tmp, file_name))
            except Exception as error:
                failed.append(f"save {file_name}: {type(error).__name__}")
        save_time = (time.perf_counter() - t0) * 1e3
    return {
        f"load {len(files)} files [ms]": load_time,
        "save [ms]": save_time,
        "loaded machines, peak [MB]": peak / 2**20,
        "failures": len(failed),
        "failed": failed,
    }


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--backend":
        print(json.dumps(run_backend(sys.argv[2])))
        return
    if len(sys.argv) == 3 and sys.argv[1] == "--files":
        print(json.dumps(run_files(sys.argv[2])))
        return
    files = {}
    for name in BACKENDS:
        out = subprocess.run(
            [sys.executable, "-m", "Tests.New.Benchmark.benchmark_backends", "--files", name],
            capture_output=True,
            text=True,
        )
        lines = [line for line in out.stdout.splitlines() if line.startswith("{")]
        if out.returncode != 0 or not lines:
            print(f"{name} files failed: {out.stderr[-2000:]}", file=sys.stderr)
            continue
        files[name] = json.loads(lines[-1])
    table = {}
    for name in BACKENDS:
        out = subprocess.run(
            [sys.executable, "-m", "Tests.New.Benchmark.benchmark_backends", "--backend", name],
            capture_output=True,
            text=True,
        )
        lines = [line for line in out.stdout.splitlines() if line.startswith("{")]
        if out.returncode != 0 or not lines:
            print(f"{name} failed:\n{out.stderr[-2000:]}", file=sys.stderr)
            continue
        table[name] = json.loads(lines[-1])
    names = list(table)
    rows = list(next(iter(table.values())))
    print("| Scenario [us] | " + " | ".join(names) + " |")
    print("|---|" + "---:|" * len(names))
    for row in rows:
        print(f"| {row} | " + " | ".join(f"{table[n].get(row, float('nan')):.1f}" for n in names) + " |")
    if files:
        names = list(files)
        print()
        print("| Machine files | " + " | ".join(names) + " |")
        print("|---|" + "---:|" * len(names))
        for row in [key for key in next(iter(files.values())) if key != "failed"]:
            print(f"| {row} | " + " | ".join(f"{files[n][row]:.1f}" for n in names) + " |")
        for name in names:
            for failure in files[name]["failed"]:
                print(f"- {name}: {failure}")


if __name__ == "__main__":
    main()
