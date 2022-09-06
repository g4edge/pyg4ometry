import sys
import re


class Card(object):
    """Card class for representing a FLUKA input card. To construct
    instances from a of FLUKA input, use the fromFree or fromFixed
    class method for FREE and FIXED format, respectively.

    """
    def __init__(self,
                 keyword,
                 what1=None, what2=None, what3=None,
                 what4=None, what5=None, what6=None,
                 sdum=None):
        self.keyword = keyword
        self.what1 = _attempt_float_coercion(what1)
        self.what2 = _attempt_float_coercion(what2)
        self.what3 = _attempt_float_coercion(what3)
        self.what4 = _attempt_float_coercion(what4)
        self.what5 = _attempt_float_coercion(what5)
        self.what6 = _attempt_float_coercion(what6)
        self.sdum = _attempt_float_coercion(sdum)

    def __repr__(self):
        return "<Card: {}>".format(self.toFreeString())

    def toList(self):
        return [self.keyword, self.what1, self.what2, self.what3,
                self.what4, self.what5, self.what6, self.sdum]

    def toFreeString(self, delim=", "):
        # Coerce to strings, replace None with empty string.
        entries = ["" if s is None else str(s) for s in self.toList()]
        return delim.join(entries)

    def nonesToZero(self):
        """Return a class instance with same contents as this
        instance, but with all entries of None set to 0.0 instead."""
        contents = self.toList()
        contents = [0 if c is None else c for c in contents]
        return Card(*contents)

    @classmethod
    def fromFree(cls, line):
        card_bits = freeFormatStringSplit(line)
        while len(card_bits) != 8:
            card_bits.append(None)
        return cls(*card_bits)

    @classmethod
    def fromFixed(cls, line):
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


def freeFormatStringSplit(string):
    """Method to split a string in FLUKA FREE format into its components."""
    # Split the string along non-black separators [,;:/\]
    partial_split = re.split(';|,|\\/|:|\\\|\n', r"{}".format(string))

    # Populate zeros between consequtive non-blank separators as per
    # the FLUKA manual.
    is_blank  = lambda s : not set(s) or set(s) == {" "}
    noblanks_split = [chunk if not is_blank(chunk) else None
                      for chunk in partial_split]

    # Strip whitespace
    components = []
    for chunk in noblanks_split:
        if chunk is None:
            components.append(None)
            continue
        components.extend(chunk.split())

    return components


def main(filein):
    c = Card(TEST_STRING)
    m = rotdefini_to_matrix(c)


if __name__ == '__main__':
    main("asdasd") #sys.argv[1])
