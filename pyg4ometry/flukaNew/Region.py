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

class Region :

    def __init__(self, name):
        self.name    = name
        self.boolean = []

    def addSubtraction(self, body):
        self.boolean.append(Subtraction(body))

    def addIntersection(self,body):
        self.boolean.append(Intersection(body))

    def addUnion(self,body):
        self.boolean.append(Union(body))

    def geant4_solid(self, reg):

        b = self.boolean[0].body.geant4_solid(reg)

        for s,i in zip(self.boolean[1:],range(0,len(self.boolean[1:])+1)):

            bName = "s"+str(i)
            print bName
            if isinstance(s,Subtraction):
                b  =_g4.solid.Subtraction(bName, b, s.body.geant4_solid(reg),[s.body.rotation(),s.body.centre()], reg)
            elif isinstance(s,Intersection):
                b  =_g4.solid.Intersection(bName, b, s.body.geant4_solid(reg),[s.body.rotation(),s.body.centre()], reg)
            elif isinstance(s,Union):
                b  =_g4.solid.Union(bName, b, s.body.geant4_solid(reg),[s.body.rotation(),s.body.centre()], reg)

        return b

