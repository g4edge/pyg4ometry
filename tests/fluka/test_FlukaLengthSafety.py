import pytest

from pyg4ometry import fluka
from pyg4ometry.fluka.body import LENGTH_SAFETY


@pytest.mark.parametrize(
    ("method", "sign"),
    [("safetyExpanded", +1), ("safetyShrunk", -1)],
)
def test_RPP_length_safety_scales_about_its_centre(method, sign):
    reg = fluka.FlukaRegistry()
    rpp = fluka.RPP("box", -10, 20, -30, 40, -50, 60, flukaregistry=reg)
    out = getattr(rpp, method)()

    # every face moves outwards (expanded) or inwards (shrunk) by the safety,
    # i.e. the box changes size but is not translated.
    assert out.lower.x == pytest.approx(rpp.lower.x - sign * LENGTH_SAFETY, rel=0, abs=1e-12)
    assert out.lower.y == pytest.approx(rpp.lower.y - sign * LENGTH_SAFETY, rel=0, abs=1e-12)
    assert out.lower.z == pytest.approx(rpp.lower.z - sign * LENGTH_SAFETY, rel=0, abs=1e-12)
    assert out.upper.x == pytest.approx(rpp.upper.x + sign * LENGTH_SAFETY, rel=0, abs=1e-12)
    assert out.upper.y == pytest.approx(rpp.upper.y + sign * LENGTH_SAFETY, rel=0, abs=1e-12)
    assert out.upper.z == pytest.approx(rpp.upper.z + sign * LENGTH_SAFETY, rel=0, abs=1e-12)
