from .. import fluka as _fluka


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
            f"beam, particle={self.particleType},\n"
            f"      energy={self.energy}*GeV,\n"
            f"      X0={self.pos[0]}*mm,\n"
            f"      Y0={self.pos[1]}*mm,\n"
            f"      Z0={self.pos[2]}*mm,\n"
            f"      Xp0={self.dir[0]}\n"
            f"      Yp0={self.dir[1]}\n"
            f"      Zp0={self.dir[2]};\n"
        )

        return s
