set(SOURCE_FILES
  Plane.h
  Polygon.h
  Vector.h
  Vertex.h
  BSPNode.h
  CSG.h
  Plane.C
  Polygon.C
  Vector.C
  Vertex.C
  BSPNode.C
  CSG.C
  )

add_library(all_test ${SOURCE_FILES})
