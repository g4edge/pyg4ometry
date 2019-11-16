import pyg4ometry.geant4 as _g4

class Subtraction:
    def __init__(self, body):
        self.body = body

class Intersection:
    def __init__(self, body):
        self.body = body

class Union:
    def __init__(self, body):
        self.body = body

class Zone : 
    def __init__(self):
        self.boolean = []
    
    def addSubtraction(self, body):
        self.boolean.append(Subtraction(body))

    def addIntersection(self,body):
        self.boolean.append(Intersection(body))    

    def centre(self):
        return self.centre

    def rotation(self):
        return self.rotation

    def geant4_solid(self, reg):

        b             = self.boolean[0].body.geant4_solid(reg)
        self.centre   = self.boolean[0].body.centre()
        self.rotation = self.boolean[0].body.rotation()

        for s,i in zip(self.boolean[1:],range(0,len(self.boolean[1:])+2)):
            bName = "s"+str(i)
            print i,bName
            if isinstance(s,Subtraction):
                b  =_g4.solid.Subtraction(bName, b, s.body.geant4_solid(reg),[s.body.rotation(),s.body.centre()], reg)
            elif isinstance(s,Intersection):
                b  =_g4.solid.Intersection(bName, b, s.body.geant4_solid(reg),[s.body.rotation(),s.body.centre()], reg)

        return b

    def fluka_free_string(self):
        fs = ""

        for s in self.boolean :
            if isinstance(s,Intersection) :
                if isinstance(s.body,Zone) :
                    fs = fs+" +("+s.body.fluka_free_string()+")"
                else :
                    fs=fs+" +"+s.body.name
            elif isinstance(s,Subtraction) :
                if isinstance(s.body,Zone) :
                    fs = fs+" -("+s.body.fluka_free_string()+")"
                else :
                    fs=fs+" -"+s.body.name
        return fs

class Region :

    def __init__(self, name):
        self.name    = name
        self.zones = []

    def addZone(self,zone):
        self.zones.append(zone)

    def centre(self):
        return self.centre

    def rotation(self):
        return self.rotation


    def geant4_solid(self, reg):

        z             = self.zones[0].geant4_solid(reg)
        self.centre   = self.zones[0].centre
        self.rotation = self.zones[0].rotation

        for z,i in zip(self.zones[1:],range(1,len(self.zones[1:])+1)):

            zName = "z"+str(i)
            print i,zName
            z  =_g4.solid.Union(zName, z, z.geant4_solid(reg),[z.rotation,z.centre], reg)

        return z

    def geant4_test(self):
        reg = _g4.Registry()
        wb  = _g4.solid.Box("world_solid",50,50,50,reg,"mm")
        wl  = _g4.LogicalVolume(wb,"G4_Galactic","world_logical",reg,True)
        fs  = self.geant4_solid(reg)
        fl  = _g4.LogicalVolume(fs,"G4_Fe","fluka_solid",reg,True)
        fp  = _g4.PhysicalVolume([0,0,0],[0,0,0],fl,"fluka_placement",wl,reg)

        return wl


    def fluka_free_string(self):
        fs = "region "+self.name

        for z in self.zones :
            fs=fs+" | "+z.fluka_free_string()

        return fs
