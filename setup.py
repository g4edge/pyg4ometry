import os
import site
import subprocess
from distutils.core import Extension, setup

from Cython.Build import cythonize

site.ENABLE_USER_SITE = True

cgal_extensions = {
    "pyg4ometry.pycgal.geom": ["src/pyg4ometry/pycgal/geom.cxx"],
    "pyg4ometry.pycgal.Point_3": ["src/pyg4ometry/pycgal/Point_3.cxx"],
    "pyg4ometry.pycgal.Point_2": ["src/pyg4ometry/pycgal/Point_2.cxx"],
    "pyg4ometry.pycgal.Vector_3": ["src/pyg4ometry/pycgal/Vector_3.cxx"],
    "pyg4ometry.pycgal.CGAL": ["src/pyg4ometry/pycgal/CGAL.cxx"],
    "pyg4ometry.pycgal.Aff_transformation_3": [
        "src/pyg4ometry/pycgal/Aff_transformation_3.cxx"
    ],
    "pyg4ometry.pycgal.Surface_mesh": ["src/pyg4ometry/pycgal/Surface_mesh.cxx"],
    "pyg4ometry.pycgal.Polyhedron_3": ["src/pyg4ometry/pycgal/Polyhedron_3.cxx"],
    "pyg4ometry.pycgal.Nef_polyhedron_3": [
        "src/pyg4ometry/pycgal/Nef_polyhedron_3.cxx"
    ],
    "pyg4ometry.pycgal.Polygon_mesh_processing": [
        "src/pyg4ometry/pycgal/Polygon_mesh_processing.cxx"
    ],
    "pyg4ometry.pycgal.Polygon_2": ["src/pyg4ometry/pycgal/Polygon_2.cxx"],
}

oce_extensions = {
    "pyg4ometry.pyoce.TCollection": ["src/pyg4ometry/pyoce/TCollection.cxx"],
    "pyg4ometry.pyoce.TKernel": ["src/pyg4ometry/pyoce/TKernel.cxx"],
    "pyg4ometry.pyoce.TDocStd": ["src/pyg4ometry/pyoce/TDocStd.cxx"],
    "pyg4ometry.pyoce.TDataStd": ["src/pyg4ometry/pyoce/TDataStd.cxx"],
    "pyg4ometry.pyoce.TNaming": ["src/pyg4ometry/pyoce/TNaming.cxx"],
    "pyg4ometry.pyoce.TDF": ["src/pyg4ometry/pyoce/TDF.cxx"],
    "pyg4ometry.pyoce.TopoDS": ["src/pyg4ometry/pyoce/TopoDS.cxx"],
    "pyg4ometry.pyoce.gp": ["src/pyg4ometry/pyoce/gp.cxx"],
    "pyg4ometry.pyoce.Geom": ["src/pyg4ometry/pyoce/Geom.cxx"],
    "pyg4ometry.pyoce.Poly": ["src/pyg4ometry/pyoce/Poly.cxx"],
    "pyg4ometry.pyoce.XCAFDoc": ["src/pyg4ometry/pyoce/XCAFDoc.cxx"],
    "pyg4ometry.pyoce.TopAbs": ["src/pyg4ometry/pyoce/TopAbs.cxx"],
    "pyg4ometry.pyoce.TopLoc": ["src/pyg4ometry/pyoce/TopLoc.cxx"],
    "pyg4ometry.pyoce.TopExp": ["src/pyg4ometry/pyoce/TopExp.cxx"],
    "pyg4ometry.pyoce.Message": ["src/pyg4ometry/pyoce/Message.cxx"],
    "pyg4ometry.pyoce.BRep": ["src/pyg4ometry/pyoce/BRep.cxx"],
    "pyg4ometry.pyoce.BRepMesh": ["src/pyg4ometry/pyoce/BRepMesh.cxx"],
    "pyg4ometry.pyoce.StlAPI": ["src/pyg4ometry/pyoce/StlAPI.cxx"],
    "pyg4ometry.pyoce.XCAFApp": ["src/pyg4ometry/pyoce/XCAFApp.cxx"],
    "pyg4ometry.pyoce.STEPCAFControl": ["src/pyg4ometry/pyoce/STEPCAFControl.cxx"],
}


def cmake_discovery():
    print("running cmake")

    os.system("mkdir .cmake")
    os.system("cp CMakeLists_setup.txt .cmake/CMakeLists.txt")
    p = subprocess.Popen(
        "cmake .",
        shell=True,
        cwd=".cmake",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()

    config = {}

    for l in out.decode("UTF-8").splitlines():
        sl = l.split()
        if sl[1] == "HAVFOUND":
            if sl[2] == "Boost":
                config["BOOST_INC"] = sl[3]
            elif sl[2] == "pybind11":
                config["PYBIND11_INC"] = sl[3].split(";")[0]
            elif sl[2] == "OpenCASCADE":
                config["OPENCASCADE_INC"] = sl[3]
                config["OPENCASCADE_LIBDIR"] = sl[4]
            elif sl[2] == "CGAL":
                config["CGAL_INC"] = sl[3]
            elif sl[2] == "MPFR":
                config["MPFR_INC"] = sl[3]
                config["MPFR_LIBDIR"] = sl[4]
                config["MPFR_LIB"] = sl[5]
            elif sl[2] == "GMP":
                config["GMP_INC"] = sl[3]
                config["GMP_LIB"] = sl[4]

    if "PYBIND11_INC" not in config.keys():
        try:
            import pybind11

            config["PYBIND11_INC"] = pybind11.get_include()
        except:
            pass

    # if boost not found inject another path
    if "BOOST_INC" not in config.keys():
        config["BOOST_INC"] = config["MPFR_INC"]

    print(config)

    os.system("rm -rf .cmake")
    return config


def pybind11_CGAL_extensions(extDict, config):
    extensions = []
    for ext in extDict:
        code = extDict[ext]
        extension = Extension(
            ext,
            include_dirs=[
                config["PYBIND11_INC"],
                config["BOOST_INC"],
                config["CGAL_INC"],
            ],
            library_dirs=[config["MPFR_LIBDIR"]],
            libraries=["mpfr", "gmp"],
            sources=code,
            language="c++",
            extra_compile_args=["-std=c++14", "-fvisibility=hidden"],
        )
        extensions.append(extension)

    return extensions


def pybind11_OCE_extensions(extDict, config):

    extensions = []
    for ext in extDict:
        code = extDict[ext]
        extension = Extension(
            ext,
            include_dirs=[config["PYBIND11_INC"], config["OPENCASCADE_INC"]],
            library_dirs=[config["OPENCASCADE_LIBDIR"]],
            libraries=[
                "TKBO",
                "TKBRep",
                "TKBin",
                "TKBinL",
                "TKBinTObj",
                "TKBinXCAF",
                "TKBool",
                "TKCAF",
                "TKCDF",
                "TKDCAF",
                "TKDraw",
                "TKFeat",
                "TKFillet",
                "TKG2d",
                "TKG3d",
                "TKGeomAlgo",
                "TKGeomBase",
                "TKHLR",
                "TKIGES",
                "TKLCAF",
                "TKMath",
                "TKMesh",
                "TKMeshVS",
                "TKOffset",
                "TKPrim",
                "TKRWMesh",
                "TKSTEP",
                "TKSTEP209",
                "TKSTEPAttr",
                "TKSTEPBase",
                "TKSTL",
                "TKService",
                "TKShHealing",
                "TKStd",
                "TKStdL",
                "TKTObj",
                "TKTopAlgo",
                "TKTopTest",
                "TKVCAF",
                "TKVRML",
                "TKViewerTest",
                "TKXCAF",
                "TKXDEDRAW",
                "TKXDEIGES",
                "TKXDESTEP",
                "TKXMesh",
                "TKXSBase",
                "TKXml",
                "TKXmlL",
                "TKXmlTObj",
                "TKXmlXCAF",
                "TKernel",
            ],
            sources=code,
            language="c++",
            extra_compile_args=["-std=c++14", "-fvisibility=hidden"],
        )
        extensions.append(extension)

    return extensions


config = cmake_discovery()

csgExts = cythonize(["src/pyg4ometry/pycsg/geom.pyx", "src/pyg4ometry/pycsg/core.pyx"])
cgalExts = pybind11_CGAL_extensions(cgal_extensions, config)
oceExts = pybind11_OCE_extensions(oce_extensions, config)

exts = []
exts.extend(csgExts)
exts.extend(cgalExts)
exts.extend(oceExts)

setup(
    # packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    ext_modules=exts,
)
