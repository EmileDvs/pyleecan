"""Legacy custom property setters, called by the legacy layers (Phase 1 only).

Some legacy properties have their own setter method (``W3 =
property(fset=_set_W3)``), with a side effect (``SlotW11._set_W3`` recomputes
W1 and W2). The generated classes inline it and list its field in
``_custom_setters``; the legacy layers (``LegacyClass``, ``LegacyModel``) call
it when the field is assigned. The setter stores the value with ``self.W3 =
value`` (``self._W3`` rewritten by the method generator): this inner assignment
is the normal validated one, the setter is not called again.
"""

_IN_CUSTOM_SETTER = set()
"""(id of the object, field name) of the custom setters being run"""


def in_custom_setter(obj, name):
    """True while the custom setter of this field runs (its inner assignment)."""
    return (id(obj), name) in _IN_CUSTOM_SETTER


def call_custom_setter(obj, name, value):
    """Assign a field through its custom setter method (_set_<name>)."""
    key = (id(obj), name)
    _IN_CUSTOM_SETTER.add(key)
    try:
        getattr(obj, "_set_" + name)(value)
    finally:
        _IN_CUSTOM_SETTER.discard(key)
