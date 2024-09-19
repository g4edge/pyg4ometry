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
            f'{self.name}: scorermesh, scoreQuantity="{self.scorer}", geometryType="{self.mesh}",\n'
        )
        scorer_mesh_string += (
            f"\t\tx={self.position[0]}*mm, y={self.position[1]}*mm, z={self.position[2]}*mm,\n"
        )
        if self.mesh == "box":
            scorer_mesh_string += (
                f"\t\tnx={self.nbins[0]}, ny={self.nbins[1]}, nz={self.nbins[2]},\n"
            )
            scorer_mesh_string += (
                f"\t\txsize={self.size[0]}*mm, ysize={self.size[1]}*mm, zsize={self.size[2]}*mm;\n"
            )
        elif self.mesh == "cyclindrical":
            scorer_mesh_string += (
                f"\t\tnr={self.nbins[0]}, nphi={self.nbins[1]}, nz={self.nbins[2]},\n"
            )
            scorer_mesh_string += f"\t\trsize={self.size[0]}*mm, zsize={self.size[2]}*mm;\n"

        fd.write(scorer_mesh_string)
