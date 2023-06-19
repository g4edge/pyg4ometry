import pyg4ometry.fluka as _fluka


class Beam:
    def __init__(self, pos=[0, 0, 0], dir=[0, 0, 1], energy=1, particleType="e-"):
        self.pos = pos
        self.dir = dir
        self.energy = energy
        self.particleType = particleType

    def flukaString(self):
        s = ""
        energySpread = 0.0
        beamDivergence = 0.0  # mrad
        beamWidthX = 0.0  # cm
        beamWidthY = 0.0  # cm
        distribType = 0.0

        flukaParticleDict = {"e-": "ELECTRON"}

        beamCard = _fluka.Card(
            "BEAM",
            -self.energy,
            energySpread,
            beamDivergence,
            beamWidthX,
            beamWidthY,
            distribType,
            flukaParticleDict[self.particleType],
        )
        beamPosCard = _fluka.Card(
            "BEAMPOS",
            self.pos[0],
            self.pos[1],
            self.pos[2],
            self.dir[0],
            self.dir[1],
            self.dir[2],
        )

        s += beamCard.toFreeString() + "\n"
        s += beamPosCard.toFreeString() + "\n"
        return s

    def bdsimString(self):
        s = (
            "beam, particle={},\n"
            "      energy={}*GeV,\n"
            "      X0={}*mm,\n"
            "      Y0={}*mm,\n"
            "      Z0={}*mm,\n"
            "      Xp0={}\n"
            "      Yp0={}\n"
            "      Zp0={};\n".format(
                self.particleType,
                self.energy,
                self.pos[0],
                self.pos[1],
                self.pos[2],
                self.dir[0],
                self.dir[1],
                self.dir[2],
            )
        )

        return s
