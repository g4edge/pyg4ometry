import ROOT as _ROOT

class Reader :

    def __init__(self, fileName):
        self.tgm = _ROOT.TGeoManager.Import(fileName)

        self.load()

    def load(self):
        self.topVolume = self.tgm.GetTopVolume()

        it = _ROOT.TGeoIterator(self.topVolume)
        n = it.Next()
        while (n):
            path = _ROOT.TString()
            it.GetPath(path)
            print(f"{it.GetLevel()} {n.GetVolume().GetShape().GetName()} {path}")
            n.Print()
            n = it.Next()