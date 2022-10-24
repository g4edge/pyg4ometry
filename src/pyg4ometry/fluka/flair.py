_flukaTemplateFileName = None

def _getFLUKATemplateFileName():
    global _flukaTemplateFileName
    if _flukaTemplateFileName is None:
        import pkg_resources
        _flukaTemplateFileName = pkg_resources.resource_filename(__name__, "flair_template.flair")
    return _flukaTemplateFileName

class Flair:
    def __init__(self, flukaInputFileName="fluka.inp", extent=None):
        self.flukaInputFileName = flukaInputFileName
        self.flukaTemplateFileName = _getFLUKATemplateFileName()

        self.extent = extent
        self.matrialColours = {}

    def write(self, fileName):
        # read template file
        inputFile = open(self.flukaTemplateFileName)
        outputFile = open(fileName, "w")

        for l in inputFile:

            # replace file name
            if l.find("_FLUKA_INPUT_FILENAME_") != -1:
                newl = l.replace("_FLUKA_INPUT_FILENAME_", self.flukaInputFileName)
                outputFile.write(newl)
            elif l.find("_FLUKA_CUSTOM_MATERIAL_INFORMATION_") != -1:
                # Material: PORTLAND
                #        alpha: 50
                #        color: #rrggbb
                # End
                newl = ""
                outputFile.write(newl)
            else:
                outputFile.write(l)

        inputFile.close()
        outputFile.close()

    def addMaterialColour(self, materialName, color=(0, 0, 0, 0)):
        if not self.materialColours.hasKey(materialName):
            self.materialColours[materialName] = color
