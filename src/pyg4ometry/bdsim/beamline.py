class Beamline:
    def __init__(self, name):
        self.name = name

        self.elements = []

    def addElement(self, element):
        self.elements.append(element)

    def write(self, fd):
        elements_string = ""
        for e in self.elements:
            if e == self.elements[-1]:
                elements_string += e.name
            else:
                elements_string += e.name + ","

        line_string = f"{self.name}: line = ({elements_string});\n"
        fd.write(line_string)

        use_string = f"use, period={self.name};\n"
        fd.write(use_string)
