class Beam:
    def __init__(self, particleName="e-", energy="16.5*GeV", pos=[0, 0, 0], dir=[0, 0, 1]):
        self.particleName = particleName
        self.energy = energy
        self.pos = pos
        self.dir = dir

    def write(self, fd):
        beam_string = f'beam, particle="{self.particleName}", energy={self.energy}, X0={self.pos[0]}, Y0={self.pos[1]}, Z0={self.pos[2]};\n'
        fd.write(beam_string)
