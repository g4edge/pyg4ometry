class Scorer:
    def __init__(
        self,
        name="score1",
        type="depositedenergy",
        parameters=None,
        conversionFactorFile=None,
        conversionFactorPath=None,
    ):
        self.name = name
        self.type = type
        self.parameters = parameters
        self.conversionFactorFile = conversionFactorFile
        self.conversionFactorPath = conversionFactorPath

    def write(self, fd):
        scorer_string = f'{self.name}: scorer, type="{self.type}"'

        if self.parameters:
            for k in self.parameters:
                scorer_string += f', {k}="{self.parameters[k]}" '

        if self.conversionFactorFile:
            scorer_string += f", conversionFactorFile={self.conversionFactorFile}"

        if self.conversionFactorPath:
            scorer_string += ", conversionFactorFile={conversionFactorFile}".format(
                conversionFactorPath=self.conversionFactorPath
            )

        scorer_string += ";\n"

        fd.write(scorer_string)


class ScorerMesh:
    def __init__(
        self,
        name,
        scorer,
        mesh="box",
        position=[0, 0, 0],
        rotation=[0, 0, 0],
        nbins=[10, 10, 10],
        size=[100, 100, 100],
    ):
        self.name = name
        self.scorer = scorer
        self.mesh = mesh
        self.position = position
        self.rotation = rotation
        self.nbins = nbins  # [nx, ny, nz] nbins in each dimension of mesh.
        self.size = size  # [xsize/rsize, ysize/0, zsize] dimensions of mesh.

    def write(self, fd):
        scorer_mesh_string = (
            '{name}: scorermesh, scoreQuantity="{scorer}", geometryType="{mesh}",\n'.format(
                name=self.name, scorer=self.scorer, mesh=self.mesh
            )
        )
        scorer_mesh_string += "\t\tx={x}*mm, y={y}*mm, z={z}*mm,\n".format(
            x=self.position[0], y=self.position[1], z=self.position[2]
        )
        if self.mesh == "box":
            scorer_mesh_string += "\t\tnx={nx}, ny={ny}, nz={nz},\n".format(
                nx=self.nbins[0], ny=self.nbins[1], nz=self.nbins[2]
            )
            scorer_mesh_string += (
                "\t\txsize={xsize}*mm, ysize={ysize}*mm, zsize={zsize}*mm;\n".format(
                    xsize=self.size[0], ysize=self.size[1], zsize=self.size[2]
                )
            )
        elif self.mesh == "cyclindrical":
            scorer_mesh_string += "\t\tnr={nr}, nphi={nphi}, nz={nz},\n".format(
                nr=self.nbins[0], nphi=self.nbins[1], nz=self.nbins[2]
            )
            scorer_mesh_string += "\t\trsize={rsize}*mm, zsize={zsize}*mm;\n".format(
                rsize=self.size[0], zsize=self.size[2]
            )

        fd.write(scorer_mesh_string)
