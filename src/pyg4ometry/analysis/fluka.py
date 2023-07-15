import struct as _struct

def fortran_skip(f):

	rlen = f.read(4)

	if not rlen:
		return 0
	(size,) = _struct.unpack("=i", rlen)
	f.seek(size, 1)
	rlen2 = f.read(4)
	if rlen != rlen2:
		raise IOError("kipping fortran blocks")
	return size


def fortran_read(f):
	rlen = f.read(4)
	if not rlen:
		return None
	(size,) = _struct.unpack("=i", rlen)
	data = f.read(size)
	rlen2 = f.read(4)
	if rlen != rlen2:
		raise IOError("reading fortran")
	return data

class _FlukaDataFile :
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

		if  data_size == 116:
			(title, time, self.weight) = _struct.unpack("=80s32sf", data)
			self.ncase  = 1
			self.nbatch = 1
		elif data_size == 120:
			(title, time, self.weight, self.ncase) = _struct.unpack("=80s32sfi", data)
			self.nbatch = 1
		elif data_size == 124:
			(title, time, self.weight,
			 self.ncase, self.nbatch) = _struct.unpack("=80s32sfii", data)
		elif data_size == 128:
			(title, time, self.weight, self.ncase, over1b, self.nbatch) = _struct.unpack("=80s32sfiii", data)

	def read_data(self, fd):
		pass


	def print_header(self):
		print("title  : ", self.title)
		print("time   : ", self.time)
		print("weight : ", self.weight)
		print("ncase  : ", self.ncase)
		print("nbatch : ", self.nbatch)


class FlukaData:
	def __init__(self, index, name, type):
		self.index = index
		self.name = name
		self.type = type
		self.data = None



class BNN(_FlukaDataFile):
	def __init__(self, fd, read_data=False):

		self.stat_pos = -1

		super().read_header(fd)
		self.read_header(fd, read_data=False)

	def read_header(self, fd, read_data=False):

		while True:
			data = fortran_read(fd)

			if data is None:
				break

			print(len(data))
			# find file location of statistics
			if len(data) == 14 and data[0:10] == b"STATISTICS":
				self.stat_pos = fd.tell()
				break

			# Parse header
			header = _struct.unpack("=i10siiffifffifffififff", data)

			print(header)

			idet = header[0]
			name = str(header[1]).strip(" ")

			e1low = float(header[4])
			e1high = float(header[5])
			selfe1n = int(header[6])
			e1d = float(header[7])

			e2low = float(header[8])
			e2high = float(header[9])
			e2n = int(header[10])
			e2d = float(header[11])

			e3low = float(header[12])
			e3high = float(header[13])
			e3n = int(header[14])
			e3d = float(header[15])

			print(e1low, e1high, e1n, e1d)
			print(e2low, e2high, e2n, e2d)
			print(e3low, e3high, e3n, e3d)

			data_size = e1n * e2n * e3n * 4

			if read_data:
				pass
			else :
				fortran_skip(fd)
	def read_data(sef, fd):
		pass


	def print_header(self):
		super().print_header()


class BNX(_FlukaDataFile):
	def __init__(self, file_name):
		pass

	def read_header(self):
		pass

	def read_data(sef, fd):
		pass


class UserDump(_FlukaDataFile):
	def __init__(self):
		pass

	def read_data(sef, fd):
		pass