class Gmad:
    def __init__(
        self, beamline=None, beam=None, options=None, samplers=None, scorers=[], scorer_meshes=[]
    ):
        self.beamline = beamline
        self.beam = beam
        self.options = options

        if type(samplers) is not list:
            samplers = [samplers]
        self.samplers = samplers

        if type(scorers) is not list:
            scorers = [scorers]
        self.scorers = scorers

        if type(scorer_meshes) is not list:
            scorer_meshes = [scorer_meshes]
        self.scorer_meshes = scorer_meshes

    def write(self, fd="test.gmad"):
        if type(fd) is str:
            fd = open(fd, "w")

        ####################################
        # write components
        ####################################
        if self.beamline:
            for e in self.beamline.elements:
                e.write(fd)

        ####################################
        # write beamline
        ####################################
        self.beamline.write(fd)

        ####################################
        # beam
        ####################################
        if self.beam:
            self.beam.write(fd)

        ####################################
        # options
        ####################################
        if self.options:
            self.options.write(fd)

        ####################################
        # samplers
        ####################################
        if len(self.samplers) > 0:
            for s in self.samplers:
                s.write(fd)

        ####################################
        # scorers
        ####################################
        if len(self.scorers) > 0:
            for s in self.scorers:
                s.write(fd)

        if len(self.scorer_meshes) > 0:
            for m in self.scorer_meshes:
                m.write(fd)

        fd.close()
