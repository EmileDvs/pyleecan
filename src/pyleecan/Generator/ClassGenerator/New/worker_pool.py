"""Process pool shared by the generators of a run.

The generators are CPU-bound pure Python (AST passes): threads are serialized
by the GIL, processes run in parallel. On Windows a worker is a new
interpreter, so the pool is started once and reused by every step of a run
(method generation, method preparation, class generation of both backends):
``run_tasks`` uses it, ``shutdown_pool`` stops it (also at exit).

The state of a step (generation dictionary, import graph...) is written once
to a pickle file; the tasks only carry its path and each worker loads it once.
Large arguments would be sent to every task, and as initializer arguments
they block the start of the workers (Windows pipes): the workers would start
one after another.
"""

import atexit
import os
import pickle
import tempfile
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.context import SpawnContext, SpawnProcess
from os import cpu_count
from uuid import uuid4

_POOL = None
_POOL_SIZE = 0

_LOADED_STATES = {}
"""Worker side: {state file: state} (the last ones only)"""

MAX_LOADED_STATES = 4


def worker_count(max_workers=None, tasks=None):
    """Number of workers to use (all the CPUs by default, at most one per task)."""
    count = max_workers if max_workers is not None else (cpu_count() or 1)
    if tasks is not None:
        count = min(count, tasks)
    return max(count, 1)


WORKER_START_TIMEOUT = 120
"""Seconds to wait for a worker to start before starting the next one"""


class _SerialStartProcess(SpawnProcess):
    """Worker process whose start returns once the worker is ready.

    Importing pyleecan.definitions reads and rewrites the user configuration
    file (legacy Functions/init_environment.get_config_dict, not atomic):
    workers importing it together read a truncated file and die
    (JSONDecodeError, BrokenProcessPool). The workers are started one after
    the other: the next one starts when the previous one has run the pool
    initializer, i.e. after its imports.
    """

    def start(self):
        super().start()
        _STARTED.acquire(timeout=WORKER_START_TIMEOUT)


class _SerialStartContext(SpawnContext):
    Process = _SerialStartProcess


_CONTEXT = _SerialStartContext()
_STARTED = _CONTEXT.Semaphore(0)
"""Released by each worker once started (pool initializer)"""


def _worker_started(started):
    """Pool initializer: the imports of the worker are done."""
    started.release()


def get_pool(max_workers):
    """The process pool of the run (started on first use)."""
    global _POOL, _POOL_SIZE
    if _POOL is not None and _POOL_SIZE == max_workers:
        return _POOL
    shutdown_pool()
    _POOL = ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=_CONTEXT,
        initializer=_worker_started,
        initargs=(_STARTED,),
    )
    _POOL_SIZE = max_workers
    return _POOL


def shutdown_pool():
    """Stop the workers of the pool (a new pool is started if needed)."""
    global _POOL, _POOL_SIZE
    if _POOL is not None:
        _POOL.shutdown(wait=True, cancel_futures=True)
    _POOL = None
    _POOL_SIZE = 0


atexit.register(shutdown_pool)


def run_tasks(function, state, arguments, max_workers=None):
    """Run ``function(state, *args)`` for each args of arguments.

    Parameters
    ----------
    function : callable
        Module-level function (imported by the workers)
    state : dict
        Data shared by the tasks (picklable)
    arguments : list
        Tuple of the arguments of each task
    max_workers : int, optional
        Number of processes (default: all the CPUs); with one worker or one
        task, the tasks run in this process

    Returns
    -------
    results : list
        Results of the tasks, in the order of arguments
    """
    arguments = list(arguments)
    workers = worker_count(max_workers, len(arguments))
    if workers <= 1:
        return [function(state, *args) for args in arguments]
    # Unique name: the workers cache the states by path
    descriptor, path = tempfile.mkstemp(
        prefix=f"pyleecan_generation_{uuid4().hex}_", suffix=".pkl"
    )
    try:
        with os.fdopen(descriptor, "wb") as state_file:
            pickle.dump(state, state_file, protocol=pickle.HIGHEST_PROTOCOL)
        pool = get_pool(workers)
        futures = [pool.submit(_run_task, function, path, args) for args in arguments]
        return [future.result() for future in futures]
    finally:
        os.remove(path)


def _run_task(function, path, args):
    """Worker side: load the state of the step (once) and run the task."""
    state = _LOADED_STATES.get(path)
    if state is None:
        if len(_LOADED_STATES) >= MAX_LOADED_STATES:
            _LOADED_STATES.clear()
        with open(path, "rb") as state_file:
            state = _LOADED_STATES[path] = pickle.load(state_file)
    return function(state, *args)
