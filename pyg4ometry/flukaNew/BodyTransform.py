

class BodyTransform(object):
    """
    Class to hold information about body transformations such as
    expansion, translation or roto-translation
    """
    def __init__(self, name, trans_type, value, flukaregistry=None):
        self.name = name
        self.trans_type = trans_type

        if trans_type == "translat":
            self.value = [float(value[0]), float(value[1]), float(value[2])]
        elif trans_type == "expansion":
            self.value = float(value)
        elif trans_type == "transform":
            self.value = str(value)
        else:
            raise ValueError("Urecognised body tranform allowed types"
                             "are 'translat', 'expansion' and 'transform'.")

        if flukaregistry is not None:
            flukaregistry.addBodyTransform(self)
