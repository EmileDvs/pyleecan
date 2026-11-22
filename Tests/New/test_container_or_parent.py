"""Container argument with the legacy parent fallback (PLAN.md Step 11)."""

import warnings

import pytest

from pyleecan.classes_common.parents import (
    ContainerFallbackWarning,
    ancestor_with,
    container_or_parent,
)


class Obj:
    def __init__(self, parent=None):
        self.parent = parent


def test_given_container():
    lam = Obj()
    assert container_or_parent(Obj(parent=Obj()), lam, "lam") is lam


def test_given_container_no_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error", ContainerFallbackWarning)
        assert container_or_parent(Obj(parent=Obj()), "lam", "lam") == "lam"
        assert container_or_parent(Obj(), None, "lam") is None  # No parent
        assert ancestor_with(Obj(), "machine") is None


def test_parent_fallback():
    lam = Obj()
    simu = Obj()
    model = Obj(parent=Obj(parent=simu))
    with pytest.warns(ContainerFallbackWarning, match="Obj: the lam argument"):
        assert container_or_parent(Obj(parent=lam), None, "lam") is lam
    with pytest.warns(ContainerFallbackWarning, match="the simu argument"):
        assert container_or_parent(model, None, "simu", depth=2) is simu
    assert container_or_parent(Obj(), None, "lam") is None
    assert container_or_parent(Obj(parent=Obj()), None, "simu", depth=3) is None
    assert container_or_parent(object(), None, "lam") is None  # No parent link


def test_check_parent_deprecated():
    from pyleecan.Functions_new.check_parent import check_parent

    obj = Obj(parent=Obj(parent=Obj()))
    with (
        pytest.warns(DeprecationWarning, match="check_parent is deprecated"),
        pytest.warns(ContainerFallbackWarning),
    ):
        assert check_parent(obj, 0) and check_parent(obj, 2)
        assert not check_parent(obj, 3)


def test_ancestor_with():
    simu = Obj()
    simu.machine = "machine"
    op = Obj(parent=Obj(parent=simu))  # OP in an input in a simulation
    with pytest.warns(ContainerFallbackWarning):
        assert ancestor_with(op, "machine") is simu
    given = Obj()
    assert ancestor_with(op, "machine", given, "simu") is given
    assert ancestor_with(op, "simu") is None
    assert ancestor_with(object(), "machine") is None  # No parent link
