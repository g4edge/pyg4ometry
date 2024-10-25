from ..visualisation import VtkViewer
from ..exceptions import NullMeshError


class ViewableMixin:
    def view(self, aabb=None):
        mesh = self.mesh(aabb=aabb)
        if mesh.isNull():
            msg = f"{self.name} mesh is null"
            raise NullMeshError(msg)
        v = VtkViewer()
        v.addMeshSimple(mesh, clip=True)  # , name=self.name)
        v.addAxes()
        v.view()
