import os as _os

class Flair :
    def __init__(self, flukaInputFileName = "fluka.inp", extent = None):
        self.flukaInputFileName    = flukaInputFileName
        self.flukaTemplateFileName = _os.path.join(_os.path.dirname(__file__), "flair_template.flair")
        self.extent = extent

    def write(self, fileName):
        # read template file
        inputFile  = open(self.flukaTemplateFileName)
        outputFile = open(fileName,"w")

        for l in inputFile :

            # replace file name
            if l.find("_FLUKA_INPUT_FILENAME_") != -1 :
                newl = l.replace("_FLUKA_INPUT_FILENAME_",self.flukaInputFileName)
                outputFile.write(newl)
            else :
                outputFile.write(l)

        inputFile.close()
        outputFile.close()



