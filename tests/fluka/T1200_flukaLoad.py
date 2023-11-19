import pyg4ometry as _pyg4


def Test(testdata):
    bnn_fileName = testdata["fluka/T1200_flukaRun001_fort.21"]
    bnx_fileName = testdata["fluka/T1200_flukaRun001_fort.22"]
    dump_fileName = testdata["fluka/T1200_flukaRun001_MGDRAW"]

    bnn_fd = open(bnn_fileName, "rb")
    _pyg4.analysis.flukaData.debugDumpFile(bnn_fd)
    bnn = _pyg4.analysis.flukaData.Usrbin(bnn_fd)

    bnx_fd = open(bnx_fileName, "rb")
    _pyg4.analysis.flukaData.debugDumpFile(bnx_fd)
    bnx = _pyg4.analysis.flukaData.Usrbin(bnx_fd)

    dump_fd = open(dump_fileName, "rb")
    _pyg4.analysis.flukaData.debugDumpFile(dump_fd)
    dump = _pyg4.analysis.flukaData.Usrdump(dump_fd, 5)

    bnn_fd.close()
    bnx_fd.close()
    dump_fd.close()
