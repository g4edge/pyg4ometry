import pyg4ometry


def Test():
    s = pyg4ometry.geant4.solid.SolidBase("oldname", "type", None)

    # get name
    name = s.name

    # set name
    s.name = "newname"

    # set name special char
    try:
        s.name = "newname!"
    except ValueError:
        pass

    # set name first char number
    try:
        s.name = "1newname"
    except ValueError:
        pass

    return {"testStatus": True}
