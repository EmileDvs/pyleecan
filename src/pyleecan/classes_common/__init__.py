"""Support shared by the Pyleecan class implementations.

The modules of this package do not depend on how the classes are implemented
(stdlib dataclasses in ``Classes_new``, pydantic models in ``Classes_pydantic``):

- ``base``: ``PyleecanBase``, marker base of every Pyleecan class base
- ``class_lookup``: module name of a class and class lookup by name
- ``class_info``: class information rebuilt from the classes (``ClassInfo``)
- ``check``: legacy value checks
- ``femm_handler``: FEMM driver used by ``MagFEMM``
- ``errors`` and ``parent_types``: generated, do not edit by hand

Each implementation package binds the lookup and ``ClassInfo`` to its own
classes (``Classes_new/_import.py``, ``Classes_new/_class_info.py``).
"""
