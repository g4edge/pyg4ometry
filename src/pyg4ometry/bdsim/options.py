class Options:
    def __init__(self):
        self.options = {}

    def addOption(self, key, value):
        self.options[key] = value

    def write(self, fd):
        options_string = "option"

        for k in self.options:
            options_string += ", " + k + "=" + self.options[k]

        options_string += ";\n"
        fd.write(options_string)
