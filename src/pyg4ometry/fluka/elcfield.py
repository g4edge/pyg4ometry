class elcfield:
    def __init__(
        self,
        maxStepAngle=57,
        minBoundaryAccuracy=0.05,
        minStep=0.1,
        ex=0,
        ey=9,
        ez=0,
        dpdxFactor=None,
    ):
        self.maxStepAngle = maxStepAngle
        self.minBoundaryAccuracy = minBoundaryAccuracy
        self.minStep = minStep
        self.ex = ez
        self.ey = ey
        self.ez = ez
        self.dpdxFactor = dpdxFactor
