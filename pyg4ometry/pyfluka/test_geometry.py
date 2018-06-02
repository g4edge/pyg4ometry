import unittest
import pyfluka
from pyfluka import vector
from pyfluka import geometry
import numpy as np
from math import pi
import os.path as _path
import pygdml
import collections

INP_PATH = _path.dirname(_path.abspath(__file__)) + "/test_input/"

class CustomAssertions(object):
    def assertExtentEqualOrClose(self, first, second):
        if not first.is_close_to(second):
            msg = "Extents not Equal!\n"
            for v in ['lower', 'upper']: # upper and lower vectors
                for comp in ['x', 'y', 'z']: # components of vector
                    first_comp = getattr(getattr(first, v), comp)
                    sec_comp = getattr(getattr(second, v), comp)
                    if first_comp != sec_comp:
                        msg += "{}.{}: {} != {}\n".format(
                            v, comp, first_comp, sec_comp)
            raise self.failureException(msg)


class TestPLA(unittest.TestCase):
    pass

# These four tests for the four possible cases when rescaling an RCC:
# None:  Neither face lies on or within the resulting zone.
# Both:  Both faces lie on or within the resulting zone.
# One:  One face lies within or on the resulting zone.
# Other: Other faces lies within or on the resulting zone.

# params = [('None', 'none', tubs_extent(50, 500, [0, pi/2, 0],
#                                        [10000., 10000., 10000.])),
#           ('Both', 'both', tubs_extent(50, 200.,
#                                        [0, pi/2, 0],
#                                        [10000., 10000., 10000.])),
#           ('One', 'one', tubs_extent(50., 250., [0, pi/2, 0],
#                                      [11250., 10000., 10000.])),
#           ('Other', 'other', tubs_extent(50., 250., [0, pi/2, 0],
#                                          [11250., 10000., 10000.]))]

# for name, param, centre in params:
#     cls_name = "TestRCC{}FacesIn".format(name)
#     globals()[cls_name] = type(cls_name, (TestRCC, unittest.TestCase), {
#         "region_name": param,
#         "centre": 1,
#         "length": 2
#     })

class TestREC(unittest.TestCase):
    pass

class TestSPH(unittest.TestCase):
    pass

class TestTRC(unittest.TestCase):
    pass

class TestXCC(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "XCC.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(400., 300., 300.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))


class TestXEC(unittest.TestCase):
    pass

class TestXYP(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "XYP.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(400., 400., 200.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))

class TestXZP(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "XZP.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(400., 200., 400.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))


class PLAMinimisation(unittest.TestCase):
    pass

class TestYCC(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "YCC.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(300., 400., 300.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))


class TestYEC(unittest.TestCase):
    pass

class TestYZP(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "YZP.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(200., 400., 400.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))

class TestZCC(unittest.TestCase):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "ZCC.inp")

    def test_crude_rescale(self):
        region = self.model.regions['min']
        boolean = region.evaluate(optimise=False)
        extent = boolean._extent()
        self.assertEqual(extent.centre, vector.Three(10000., 10000., 10000.))
        self.assertEqual(extent.length, vector.Three(300., 300., 400.))

    def test_rescaled_mesh(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()
        self.assertEqual(unopt_extent, opt_extent)

    def test_minimisation(self):
        region = self.model.regions['min']

        unopt = region.evaluate(optimise=False)
        opt = region.evaluate(optimise=True)

        unopt_extent = unopt._extent()
        opt_extent = opt._extent()

        areless = []
        for opt_solid, unopt_solid in zip(
                opt.gdml_primitives(),
                unopt.gdml_primitives()):
            areless.append(solid_less_than(opt_solid, unopt_solid))
        self.assertTrue(any(areless))


class TestZEC(unittest.TestCase):
    pass

class TestRemoveRedundantBodies(unittest.TestCase, CustomAssertions):
    def setUp(self):
        self.model = pyfluka.model.Model(INP_PATH + "redundant_body.inp")

    def test_remove_redundant_yzp(self):
        opt = self.model.regions['yzp'].evaluate(optimise=True)
        unopt =  self.model.regions['yzp'].evaluate(optimise=False)

        opt_extent = opt._extent()
        unopt_extent = unopt._extent()

        opt_gdml_count = len(opt.gdml_primitives())
        unopt_gdml_count = len(unopt.gdml_primitives())
        # Just testing the thickness.  The area of the infinite plane
        # will not be the same due to changes in the auto-scaling, but
        # that is OK.
        self.assertEqual(opt_extent.lower.x, unopt_extent.lower.x)
        self.assertEqual(opt_extent.upper.x, unopt_extent.upper.x)
        self.assertLess(opt_gdml_count, unopt_gdml_count)

    def test_remove_redundant_xzp(self):
        opt = self.model.regions['xzp'].evaluate(optimise=True)
        unopt =  self.model.regions['xzp'].evaluate(optimise=False)

        opt_extent = opt._extent()
        unopt_extent = unopt._extent()

        opt_gdml_count = len(opt.gdml_primitives())
        unopt_gdml_count = len(unopt.gdml_primitives())
        # Just testing the thickness.  The area of the infinite plane
        # will not be the same due to changes in the auto-scaling, but
        # that is OK.
        self.assertEqual(opt_extent.lower.y, unopt_extent.lower.y)
        self.assertEqual(opt_extent.upper.y, unopt_extent.upper.y)
        self.assertLess(opt_gdml_count, unopt_gdml_count)

    def test_remove_redundant_xyp(self):
        opt = self.model.regions['xyp'].evaluate(optimise=True)
        unopt =  self.model.regions['xyp'].evaluate(optimise=False)

        opt_extent = opt._extent()
        unopt_extent = unopt._extent()

        opt_gdml_count = len(opt.gdml_primitives())
        unopt_gdml_count = len(unopt.gdml_primitives())
        # Just testing the thickness.  The area of the infinite plane
        # will not be the same due to changes in the auto-scaling, but
        # that is OK.
        self.assertEqual(opt_extent.lower.z, unopt_extent.lower.z)
        self.assertEqual(opt_extent.upper.z, unopt_extent.upper.z)
        self.assertLess(opt_gdml_count, unopt_gdml_count)

    def test_remove_redundant_RPP(self):
        opt = self.model.regions['rpp'].evaluate(optimise=True)
        unopt =  self.model.regions['rpp'].evaluate(optimise=False)

        opt_extent = opt._extent()
        unopt_extent = unopt._extent()

        self.assertEqual(opt_extent, unopt_extent)
        self.assertIsInstance(opt, geometry.RPP)
        self.assertIsInstance(unopt, geometry.Boolean)

def solid_less_than(solid1, solid2):
    try:
        return (solid1.pX < solid2.pX
                or solid1.pY < solid2.pY
                or solid1.pZ < solid2.pZ)
    except AttributeError:
        pass

    try:
        return solid1.pDz < solid2.pDz
    except AttributeError:
        pass

    return None

if __name__ == '__main__':
    unittest.main()
