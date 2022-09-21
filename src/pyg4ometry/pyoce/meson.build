pyoceExtensionMods = {'TCollection':['TCollection.cxx'],
		      'TKernel':['TKernel.cxx'],
		      'TDocStd':['TDocStd.cxx'],
		      'TDataStd':['TDataStd.cxx'],
		      'TNaming':['TNaming.cxx'],
		      'TDF':['TDF.cxx'],
		      'TopoDS':['TopoDS.cxx'],
		      'gp':['gp.cxx'],
		      'Geom':['Geom.cxx'],
		      'Poly':['Poly.cxx'],
		      'XCAFDoc':['XCAFDoc.cxx'],
		      'TopAbs':['TopAbs.cxx'],
		      'TopLoc':['TopLoc.cxx'],
		      'TopExp':['TopExp.cxx'],
		      'Message':['Message.cxx'],
		      'BRep':['BRep.cxx'],
		      'BRepMesh':['BRepMesh.cxx'],
		      'StlAPI':['StlAPI.cxx'],
		      'XCAFApp':['XCAFApp.cxx'],
		      'STEPCAFControl':['STEPCAFControl.cxx']}

foreach mod, srcs : pyoceExtensionMods
	py3.extension_module(mod,srcs,
			     dependencies : [pybind11, oceDep],
			     cpp_args : ['-fvisibility=hidden','-std=c++14'])
endforeach

