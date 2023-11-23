class mgnfield:
    def __init__(self, maxStepAngle=57, minBoundaryAccuracy=0.05, minStep=0.1, bx=0, by=9, bz=0):
        self.maxStepAngle = maxStepAngle
        self.minBoundaryAccuracy = minBoundaryAccuracy
        self.minStep = minStep
        self.bx = bz
        self.by = by
        self.bz = bz


class mgnfield_mgncreat:
    def __init__(
        self,
        fieldStrength=1,
        rotDefi=None,
        regionLattice=0,
        lowerRegion=None,
        upperRegion=None,
        stepRegion=1,
        fieldName="field",
    ):
        self.fieldStrength = fieldStrength
        self.rotDefi = rotDefi
        self.regionLattice = regionLattice
        self.lowerRegion = lowerRegion
        self.upperRegion = upperRegion
        self.stepRegion = stepRegion
        self.fieldName = fieldName


class mgncreat:
    def __init__(
        self,
        analyticalField=0,
        interpolatedField=0,
        interpolationRadius=0,
        xoffset=0,
        yoffset=0,
        xsym=0,
        ysym=0,
        zsym=0,
        fieldName=None,
    ):
        self.analyticalField = analyticalField
        self.interpolatedField = interpolatedField
        self.interpolationRadius = interpolationRadius
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.xsym = xsym
        self.ysym = ysym
        self.zsym = zsym
        self.fieldName = fieldName


class mgndata_array:
    def __init__(self, mgndata, fieldName):
        self.mgndata = mgndata
        self.fieldName = fieldName
