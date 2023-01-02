from pyg4ometry.exceptions import NullMeshError
from pyg4ometry.visualisation import VtkViewer


class ViewableMixin:
    def view(self, aabb=None):
        mesh = self.mesh(aabb=aabb)
        if mesh.isNull():
            raise NullMeshError(f"{self.name} mesh is null")
        v = VtkViewer()
        v.addMeshSimple(mesh, clip=True)  # , name=self.name)
        v.addAxes()
        v.view()
