import pyg4ometry as _pyg4


def Test(testdata):
    usr_fileName = testdata["fluka/T1200_flukaRun001_fort.21"]
    dump_fileName = testdata["fluka/T1200_flukaRun001_MGDRAW"]

    usr_fd = open(usr_fileName, "rb")
    usr = _pyg4.analysis.flukaData.Usrbin(usr_fd)

    dump_fd = open(dump_fileName, "rb")
    dump = _pyg4.analysis.flukaData.Usrdump(dump_fd, 5)

    usr_fd.close()
    dump_fd.close()
