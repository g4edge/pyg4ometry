class SolidBase(object):
        @property
        def name(self):
            return self._name

        @name.setter
        def name(self, name):
            non_alphanum = set([c for c in name if not c.isalnum()])
            non_alphanum = non_alphanum.difference('_') # underscors are # OK.
            if non_alphanum:
                msg = "Forbidden character(s) in name \"{}\": {}.".format(
                    name, list(non_alphanum))
                raise ValueError(msg)
            if not name[0].isalpha():
                msg = "First char of name \"{}\" must be a letter.".format(name)
                raise ValueError(msg)
            self._name = name
