"""Lists and dicts setting the legacy parent link of the objects they receive.

The legacy getters of the list and dict properties set the parent of their
items on each read, so that an object appended to the list gets its parent
(``lam.hole.append(HoleM50())``). The legacy layers (``LegacyClass``,
``LegacyModel``) store these fields in a ``ParentList`` / ``ParentDict``
instead: the parent is set when an item is added, without a cost on reads.

The owner is held by a weak reference (no reference cycle for the garbage
collector). Copies and pickles are plain lists and dicts (the owner is not
copied); the legacy layer wraps them again when they are assigned to a field.
"""

from weakref import ref

from .base import PyleecanBase


def set_parent(item, owner):
    """Set the parent of a Pyleecan object (other values are ignored)."""
    if not isinstance(item, PyleecanBase):
        return
    if "parent" in getattr(item, "__dataclass_fields__", ()):
        object.__setattr__(item, "parent", owner)  # Plain field: no validation
    elif hasattr(item, "parent"):
        item.parent = owner  # Pydantic: private attribute behind a property


def _no_owner():
    """Owner of a container not held by an object."""
    return None


class ParentList(list):
    """List setting the parent of the objects added to it."""

    __slots__ = ("_owner",)

    def __init__(self, items=(), owner=None):
        # The items given here get their parent from the legacy layer, which
        # also checks their parent type: only the added items are set here
        super().__init__(items)
        self._owner = ref(owner) if owner is not None else _no_owner

    def append(self, item):
        set_parent(item, self._owner())
        super().append(item)

    def insert(self, index, item):
        set_parent(item, self._owner())
        super().insert(index, item)

    def extend(self, items):
        items = list(items)
        for item in items:
            set_parent(item, self._owner())
        super().extend(items)

    def __iadd__(self, items):
        self.extend(items)
        return self

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            value = list(value)
            for item in value:
                set_parent(item, self._owner())
        else:
            set_parent(value, self._owner())
        super().__setitem__(index, value)

    def __reduce_ex__(self, protocol):  # copy, deepcopy and pickle: a list
        return (list, (list(self),))


class ParentDict(dict):
    """Dict setting the parent of the objects added to it."""

    __slots__ = ("_owner",)

    def __init__(self, items=(), owner=None):
        # The items given here get their parent from the legacy layer, which
        # also checks their parent type: only the added items are set here
        super().__init__(items)
        self._owner = ref(owner) if owner is not None else _no_owner

    def __setitem__(self, key, value):
        set_parent(value, self._owner())
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def __reduce_ex__(self, protocol):  # copy, deepcopy and pickle: a dict
        return (dict, (dict(self),))


def with_parent(value, owner):
    """The value of a field, its list or dict wrapped to set the parents."""
    if type(value) is list:
        return ParentList(value, owner)
    if type(value) is dict:
        return ParentDict(value, owner)
    return value
