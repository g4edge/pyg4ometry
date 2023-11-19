class Sampler:
    def __init__(self, range=None, type=None):
        self.range = range
        self.type = type

    def write(self, fd):
        if self.range is not None and self.type is None:
            sampler_string = f"sample, range={self.range};\n"
        elif self.range is None and self.type is not None:
            sampler_string = f"sample, {self.type};\n"

        fd.write(sampler_string)
