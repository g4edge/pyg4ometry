class Element:
    def __init__(self, name, type, **kwargs):
        self.name = name
        self.type = type
        self.kwargs = kwargs

    def write(self, fd):
        element_string = f"{self.name}: {self.type}"
        for k in self.kwargs:
            element_kwargs = "," + k + "=" + self.kwargs[k]
            element_string += element_kwargs
        element_string += ";\n"

        fd.write(element_string)
