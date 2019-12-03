import sys


TEST_STRING = "ROT-DEFI                   45.       45.       50.       50.       50.bb1rotdefi"



class Card(object):
    def __init__(self, line): # fixed format only.
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

        self._columns = columns
        self.keyword = columns[0]
        self.what1 = columns[1]
        self.what2 = columns[2]
        self.what3 = columns[3]
        self.what4 = columns[4]
        self.what5 = columns[5]
        self.what6 = columns[6]
        self.sdum = columns[7]

    def __repr__(self):
        if self.keyword is not None:
            return "<Card: {}: {}>".format(self.keyword, self._columns[1:])
        raise TypeError("keyword=None  for continuation cards only and"
                        " don't support that yet.")


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


def main(filein):
    c = Card(TEST_STRING)
    m = rotdefini_to_matrix(c)


if __name__ == '__main__':
    main("asdasd") #sys.argv[1])
