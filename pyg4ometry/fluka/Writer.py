class Writer :

    def __init__(self):
        pass

    def addDetector(self, flukaRegistry):
        self.flukaRegistry = flukaRegistry

    def write(self, fileName):
        f = open(fileName,"w")

        f.write("GEOBEGIN                                                              COMBNAME\n")
        f.write("    0    0                                                                    \n")
        # loop over bodies
        for bk in self.flukaRegistry.bodyDict.keys() :
            f.write(self.flukaRegistry.bodyDict[bk].flukaFreeString()+"\n")
        f.write("END\n")

        # loop over regions
        for rk in self.flukaRegistry.regionDict.keys() :
            f.write(self.flukaRegistry.regionDict[rk].flukaFreeString()+"\n")
        f.write("END\n")
        f.write("GEOEND\n")


        f.close()

