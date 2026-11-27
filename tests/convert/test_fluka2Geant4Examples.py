from pathlib import Path

import pytest

import pyg4ometry.config as _config
from pyg4ometry import convert, fluka, gdml

_exampleFiles = [
    "fluka/TCC2-TDC85_tunnels_3.inp",
    "fluka/TCC2-TDC85_tunnels_T4.inp",
]


def _daughterNames(reg):
    return sorted(pv.logicalVolume.name for pv in reg.getWorldVolume().daughterVolumes)


def convertExample(inputPath, outputPath):
    """Convert a FLUKA input file and write GDML and a BDSIM gmad tester to outputPath."""
    greg = convert.fluka2Geant4(fluka.Reader(inputPath).flukaregistry)
    assert greg.getWorldVolume().daughterVolumes

    # The gmad refers to the GDML by name, so both are written to the same directory.
    gdmlName = Path(inputPath).stem + ".gdml"
    w = gdml.Writer()
    w.addDetector(greg)
    w.write(Path(outputPath) / gdmlName)
    w.writeGmadTester(Path(outputPath) / (Path(inputPath).stem + ".gmad"), gdmlName)

    # Read back, so the converted geometry must be valid GDML.
    reread = gdml.Reader(Path(outputPath) / gdmlName).getRegistry()
    assert _daughterNames(reread) == _daughterNames(greg)
    return greg


@pytest.mark.parametrize("fileName", _exampleFiles)
def test_fluka2Geant4_example_gdml(testdata, tmptestdir, monkeypatch, fileName):
    # Meshing is most of the conversion time and is not needed to write GDML.
    monkeypatch.setattr(_config, "doMeshing", False)
    convertExample(testdata[fileName], tmptestdir)


@pytest.mark.slow
@pytest.mark.parametrize("fileName", _exampleFiles)
def test_fluka2Geant4_example_overlaps(testdata, fileName):
    greg = convert.fluka2Geant4(fluka.Reader(testdata[fileName]).flukaregistry)

    nOverlaps = [0]  # Counter filled by checkOverlaps.
    greg.getWorldVolume().checkOverlaps(recursive=True, nOverlapsDetected=nOverlaps)
    assert nOverlaps[0] == 0


# Example: write the GDML and gmad tester for one file to the current directory.
# from g4edgetestdata import G4EdgeTestData
# data = G4EdgeTestData()
# convertExample(data["fluka/TCC2-TDC85_tunnels_3.inp"], Path.cwd())
