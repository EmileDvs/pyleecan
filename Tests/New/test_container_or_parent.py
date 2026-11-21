"""Container argument with the legacy parent fallback (PLAN.md Step 11)."""

from pyleecan.classes_common.parents import container_or_parent


class Obj:
    def __init__(self, parent=None):
        self.parent = parent


def test_given_container():
    lam = Obj()
    assert container_or_parent(Obj(parent=Obj()), lam, "lam") is lam


def test_parent_fallback():
    lam = Obj()
    simu = Obj()
    model = Obj(parent=Obj(parent=simu))
    assert container_or_parent(Obj(parent=lam), None, "lam") is lam
    assert container_or_parent(model, None, "simu", depth=2) is simu
    assert container_or_parent(Obj(), None, "lam") is None
    assert container_or_parent(Obj(parent=Obj()), None, "simu", depth=3) is None
    assert container_or_parent(object(), None, "lam") is None  # No parent link
