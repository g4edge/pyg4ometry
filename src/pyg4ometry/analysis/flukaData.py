import struct as _struct
import numpy as _np


def fortran_skip(f):
    rlen = f.read(4)

    if not rlen:
        return 0
    (size,) = _struct.unpack("=i", rlen)
    f.seek(size, 1)
    rlen2 = f.read(4)
    if rlen != rlen2:
        msg = "kipping fortran blocks"
        raise OSError(msg)
    return size


def fortran_read(f):
    rlen = f.read(4)
    if not rlen:
        return None
    (size,) = _struct.unpack("=i", rlen)
    data = f.read(size)
    rlen2 = f.read(4)
    if rlen != rlen2:
        msg = "reading fortran"
        raise OSError(msg)
    return data


def debugDumpFile(fd, limit=10000000):
    fd.seek(0)

    iData = 0
    data = True

    while data:
        data = fortran_read(fd)
        if data and iData < limit:
            print(iData, len(data))
        iData += 1

    print("total records", iData)


class _FlukaDataFile:
    def __init__(self, fd):
        self.title = None
        self.time = None
        self.weight = None
        self.ncase = None
        self.nbatch = None

        self.read_header(fd)

    def read_header(self, fd):
        data = fortran_read(fd)

        data_size = len(data)

        if data_size == 116:
            (self.title, self.time, self.weight) = _struct.unpack("=80s32sf", data)
            self.ncase = 1
            self.nbatch = 1
        elif data_size == 120:
            (self.title, self.time, self.weight, self.ncase) = _struct.unpack("=80s32sfi", data)
            self.nbatch = 1
        elif data_size == 124:
            (self.title, self.time, self.weight, self.ncase, self.nbatch) = _struct.unpack(
                "=80s32sfii", data
            )
        elif data_size == 128:
            (
                self.title,
                self.time,
                self.weight,
                self.ncase,
                over1b,
                self.nbatch,
            ) = _struct.unpack("=80s32sfiii", data)

    def read_data(self, fd):
        pass

    def print_header(self):
        print("title  : ", self.title)
        print("time   : ", self.time)
        print("weight : ", self.weight)
        print("ncase  : ", self.ncase)
        print("nbatch : ", self.nbatch)


class FlukaBinData:
    def __init__(self, index, name, type):
        self.index = index
        self.name = name
        self.type = type
        self.data = None
        self.stats = None

    def binToVtkGrid(self):
        import vtk as _vtk
        import vtk.util.numpy_support as _numpy_support

        # rectilinear
        if self.mesh == 0:
            imdata = _vtk.vtkImageData()
            dataArray = _numpy_support.numpy_to_vtk(
                _np.log10(self.data.ravel()), deep=True, array_type=_vtk.VTK_DOUBLE
            )

            print(_np.log10(self.data.ravel()).min(), _np.log10(self.data.ravel()).max())
            ox = -(self.e1high - self.e1low) / 2 * 10
            oy = -(self.e2high - self.e2low) / 2 * 10
            oz = -(self.e3high - self.e3low) / 2 * 10
            print("origin", ox, oy, oz)
            dx = (self.e1high - self.e1low) / self.e1n * 10
            dy = (self.e2high - self.e2low) / self.e2n * 10
            dz = (self.e3high - self.e3low) / self.e3n * 10

            imdata.SetDimensions(self.data.shape)
            imdata.SetSpacing([dx, dy, dz])
            imdata.SetOrigin([ox, oy, oz])
            imdata.GetPointData().SetScalars(dataArray)

            return imdata

        # cylindrical
        elif self.mesh == 1:
            pass


class FlukaBdxData:
    def __init__(self, index, name, type):
        self.index = index
        self.name = name
        self.type = type


class Usrbin(_FlukaDataFile):
    def __init__(self, fd, read_data=False):
        fd.seek(0)

        self.stat_pos = -1

        self.detector = []

        super().read_header(fd)
        self.read_file(fd)

    def read_file(self, fd):
        while self.read_header(fd):
            self.read_data(fd)
        print(f"Read {len(self.detector)} detectors")

        self.read_stats(fd)

    def read_data(self, fd):
        self.detector[-1].data = _np.reshape(
            _np.frombuffer(fortran_read(fd), _np.float32),
            (self.detector[-1].e1n, self.detector[-1].e2n, self.detector[-1].e3n),
            order="F",
        )

    def read_stats(self, fd):
        data = fortran_read(fd)
        if data is None:
            print("No statistics")
            return

        if len(data) == 14 and data[0:10] == b"STATISTICS":
            self.stat_pos = fd.tell()

        print("Statistics present")
        for det in self.detector:
            data = fortran_read(fd)
            det.errors = _np.reshape(
                _np.frombuffer(data, _np.float32), (det.e1n, det.e2n, det.e3n), order="F"
            )

    def read_header(self, fd):
        pos = fd.tell()
        data = fortran_read(fd)

        if data is None:
            return False

        if len(data) != 86:
            fd.seek(pos)  # return to statistics
            return False

        # Parse header
        header = _struct.unpack("=i10siiffifffifffififff", data)

        idet = header[0]
        name = str(header[1]).replace("'", "").strip(" ")
        mesh = int(header[2])
        e1low = float(header[4])
        e1high = float(header[5])
        e1n = int(header[6])
        e1d = float(header[7])

        e2low = float(header[8])
        e2high = float(header[9])
        e2n = int(header[10])
        e2d = float(header[11])

        e3low = float(header[12])
        e3high = float(header[13])
        e3n = int(header[14])
        e3d = float(header[15])

        # print(e1low, e1high, e1n, e1d)
        # print(e2low, e2high, e2n, e2d)
        # print(e3low, e3high, e3n, e3d)

        data_size = e1n * e2n * e3n * 4

        fluka_data = FlukaBinData(idet, name, "bin")

        fluka_data.ncase = self.ncase
        fluka_data.nbatch = self.nbatch
        fluka_data.weight = self.weight
        fluka_data.mesh = mesh

        fluka_data.e1low = e1low
        fluka_data.e1high = e1high

        fluka_data.e2low = e2low
        fluka_data.e2high = e2high

        fluka_data.e3low = e3low
        fluka_data.e3high = e3high

        fluka_data.e1n = e1n
        fluka_data.e2n = e2n
        fluka_data.e3n = e3n

        self.detector.append(fluka_data)

        return True

    def print_header(self):
        super().print_header()


class Usrbdx(_FlukaDataFile):
    def __init__(self, file):
        self.detector = []

        if type(file) is str:
            fd = open(file, "rb")
        else:
            fd = file
            fd.seek(0)

        super().read_header(fd)
        self.read_file(fd)

    def read_file(self, fd):
        while self.read_header(fd):
            self.read_data(fd)

        self.read_stats(fd)

    def read_data(self, fd):
        self.detector[-1].data = _np.reshape(
            _np.frombuffer(fortran_read(fd), _np.float32),
            (self.detector[-1].ne, self.detector[-1].na),
            order="F",
        )

    def read_stats(self, fd):
        data = fortran_read(fd)
        if data is None:
            print("No statistics")
            return

        if len(data) == 14 and data[0:10] == b"STATISTICS":
            self.stat_pos = fd.tell()

        # 6 data records
        # 0 : total, error
        # 1 :

        for det in self.detector:
            data = fortran_read(fd)

            data = _struct.unpack("=%df" % (len(data) // 4), data)
            det.total = data[0]
            det.totalError = data[1]

            det.error = []
            for i in range(6):
                data = fortran_read(fd)
                det.error.append(_struct.unpack("=%df" % (len(data) // 4), data))

    def read_header(self, fd):
        pos = fd.tell()

        data = fortran_read(fd)
        if not data:
            return False

        if len(data) != 78:
            fd.seek(pos)  # return to statistics
            return False

        header = _struct.unpack("=i10siiiifiiiffifffif", data)

        num = header[0]
        name = header[1]
        type = header[2]

        fluka_data = FlukaBdxData(num, name, type)

        fluka_data.dist = header[3]
        fluka_data.reg1 = header[4]
        fluka_data.reg2 = header[5]
        fluka_data.area = header[6]
        fluka_data.twoway = header[7]
        fluka_data.fluence = header[8]
        fluka_data.lowneu = header[9]
        fluka_data.elow = header[10]
        fluka_data.ehigh = header[11]
        fluka_data.ne = header[12]
        fluka_data.de = header[13]
        fluka_data.alow = header[14]
        fluka_data.ahigh = header[15]
        fluka_data.na = header[16]
        fluka_data.da = header[17]

        self.detector.append(fluka_data)

        return True


class Usrdump(_FlukaDataFile):
    def __init__(self, fd, iEventHeaderToRead=10000):
        self.event_seek = []
        self.read_structure(fd, iEventHeaderToRead)

        self.track_data = []
        self.energy_data = []
        self.source_data = []

    def read_structure(self, fd, iEventHeaderToRead=10000):
        print("read_header")

        # start of file
        fd.seek(0)

        # count of file records
        iRecord = 0
        iEvent = 0

        while True:
            # file position for later recording
            file_pos = fd.tell()

            # read file record
            data = fortran_read(fd)

            # if nothing is read break loop
            if not data:
                break

            # entry header
            if len(data) == 20:
                ndum, mdum, jdum, edum, wdum = _struct.unpack("=iiiff", data)

                # print(ndum, mdum, jdum, edum, wdum)
                if ndum < 0:
                    print(iRecord, file_pos, "read source")
                    self.event_seek.append(file_pos)
                    if iEvent > iEventHeaderToRead:
                        break

                    iEvent += 1
                    iRecord += 1

                # skip data
                fortran_read(fd)

        self.event_seek.append(100000000000)

    def read_event(self, fd, ievent=0):
        print("read_event")
        # clear event data
        self.track_data.clear()
        self.energy_data.clear()
        self.source_data.clear()

        # check event number
        if ievent > len(self.event_seek) - 1:
            print("Event out of range")
            return

        # move to start of event
        fd.seek(self.event_seek[ievent])

        # read header
        while True:
            if fd.tell() == self.event_seek[ievent + 1]:
                print("next event reached", fd.tell())
                break

            # read file record
            data = fortran_read(fd)

            # break on no data
            if not data:
                break

            if len(data) == 20:
                ndum, mdum, jdum, edum, wdum = _struct.unpack("=iiiff", data)

                # tracking
                if ndum > 0:
                    ntrack = ndum
                    mtrack = mdum
                    jtrack = jdum
                    etrack = edum
                    wtrack = wdum
                    data = fortran_read(fd)
                    data = list(_struct.unpack("=%df" % (3 * (ntrack + 1) + mtrack + 1), data))
                    self.track_data.append(data)
                # energy
                elif ndum == 0:
                    icode = ndum
                    jtrack = jdum
                    etrack = edum
                    wtrack = wdum
                    data = fortran_read(fd)
                    data = list(_struct.unpack("=4f", data))
                    self.energy_data.append(data)
                # source
                else:
                    ncase = ndum
                    npflka = mdum
                    nstmax = jdum
                    tkesum = edum
                    weipri = wdum
                    data = fortran_read(fd)
                    data = list(_struct.unpack("=" + ("i8f" * npflka), data))
                    self.source_data.append(data)

    def trackDataToPolydata(self):
        import vtk as _vtk

        vp = _vtk.vtkPoints()
        ca = _vtk.vtkCellArray()
        pd = _vtk.vtkPolyData()

        iPnt = 0
        for t in self.track_data:
            iPntStart = iPnt
            id1 = vp.InsertNextPoint(10 * t[0], 10 * t[1], 10 * t[2])
            id2 = vp.InsertNextPoint(10 * t[3], 10 * t[4], 10 * t[5])

            iPnt += 2

            ca.InsertNextCell(2)
            ca.InsertCellPoint(id1)
            ca.InsertCellPoint(id2)

        pd.SetPoints(vp)
        pd.SetLines(ca)

        return pd
