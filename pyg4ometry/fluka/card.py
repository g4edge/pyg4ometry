import sys


FIXED = "ROT-DEFI                   45.       45.       50.       50.       50.bb1rotdefi"
FREE = "ROT-DEFI  , 927002., 0.0, 0.0, 0.0, 0.0, 0., XXTb413"

class Card(object):
    """Card class for representing a FLUKA input card. To construct
    instances from a of FLUKA input, use the from_free or from_fixed
    class method for FREE and FIXED format, respectively.

    """
    def __init__(self, keyword, what1, what2, what3, what4, what5, what6, sdum):
        self.keyword = keyword
        self.what1 = what1
        self.what2 = what2
        self.what3 = what3
        self.what4 = what4
        self.what5 = what5
        self.what6 = what6
        self.sdum = sdum

    def __repr__(self):
        return self.to_free_string()

    def as_list(self):
        return [self.keyword, self.what1, self.what2, self.what3,
                self.what4, self.what5, self.what6, self.sdum]

    def to_free_string(self, delim=","):
        # Coerce to strings, replace None with empty string.
        entries = ["" if s is None else str(s) for s in self.as_list()]
        return delim.join(entries)

    @classmethod
    def from_free(cls, line):
        return cls(*free_format_string_split(line))

    @classmethod
    def from_fixed(cls, line):
        if len(line) > 80:
            raise TypeError("Line too long.  Maximum line length is 80.")
        line = line.rstrip('\n')
        # column positions are multiples of 10 up to 80 inclusive.
        positions = [10 * x for x in range(9)]
        # Split the line into a list of strings according to the positions
        columns = [line[start:stop]
                   for start, stop in zip(positions, positions[1:])]
        # remove trailing/leading whitepace
        columns = [column.strip() for column in columns]
        # Empty strings -> None
        columns = [column if column != "" else None for column in columns]
        columns = [_attempt_float_coercion(column) for column in columns]

        return cls(*columns)


def _attempt_float_coercion(string):
    try:
        return float(string)
    # (Not a coercable string, not a coercable type)
    except (ValueError, TypeError):
        return string

def rotdefini_to_matrix(card):
    if keyword != "ROT-DEFI":
        raise ValueError("Not a ROT-DEFI card.")

    if card.what1 is not None:
        raise ValueError("non-default value for WHAT(1) is not supported.")

    from IPython import embed; embed()

def free_format_string_split(string):
    """Method to split a string in FLUKA FREE format into its components."""
    # Split the string along non-black separators [,;:/\]
    partial_split = _re.split(';|,|\\/|:|\\\|\n', r"{}".format(string))

    # Populate zeros between consequtive non-blank separators as per
    # the FLUKA manual.
    is_blank  = lambda s : not set(s) or set(s) == {" "}
    noblanks_split = [chunk if not is_blank(chunk) else '0.0'
                      for chunk in partial_split]

    # Split along whitespaces now for complete result.
    components = []
    for chunk in noblanks_split:
        components += chunk.split()

    return components


def main(filein):
    c = Card(TEST_STRING)
    m = rotdefini_to_matrix(c)


if __name__ == '__main__':
    main("asdasd") #sys.argv[1])
