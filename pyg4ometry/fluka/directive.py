from collections import MutableSequence
import numbers
from operator import mul

import numpy as np

from pyg4ometry.transformation import reverse
from pyg4ometry.exceptions import FLUKAError
from .vector import Three
from .card import Card


class Transform(object):
    """expansion, translation, rotoTranslation can be either a single
    instance of RotoTranslation or a multiple instances of
    RotoTranslation and RecursiveRotoTranslation"""
    def __init__(self, expansion=None, translation=None, rotoTranslation=None):
        self.expansion = expansion
        self.translation = translation
        self.rotoTranslation = rotoTranslation

    def leftMultiplyVector(self, vector):
        vector4d = [vector[0], vector[1], vector[2], 1] # [x, y, z, 1]
        matrix = self.to4DMatrix()
        return Three(matrix.dot(vector4d)[0:3])

    def leftMultiplyRotation(self, matrix):
        matrices = self._rotoTranslationsTo4DMatrices()
        combinedMatrix = _rightMultiplyMatrices(matrices)
        return combinedMatrix[:3, :3].dot(matrix)

    def netExpansion(self):
        if not self.expansion:
            return 1.0
        elif isinstance(self.expansion, numbers.Number):
            return self.expansion
        return reduce(mul, self.expansion, 1.)

    def _expansionsTo4DMatrices(self):
        if not self.expansion:
            return [_expansionFactorTo4DMatrix(1.0)]
        if isinstance(self.expansion, numbers.Number):
            return [_expansionFactorTo4DMatrix(self.expansion)]
        # Then it is a list of expansions
        return [_expansionFactorTo4DMatrix(m) for m in self.expansion]

    def _translationsTo4DMatrices(self):
        if not self.translation:
            return [np.identity(4)]
        if isinstance(self.translation[0], numbers.Number):
            # Then it's just a single translation I assume
            return [_translationTo4DMatrix(self.translation[0])]
        # Then it's a list of translations
        return [_translationTo4DMatrix(m) for m in self.translation]

    def _rotoTranslationsTo4DMatrices(self):
        if not self.rotoTranslation:
            return [np.identity(4)]
        try: # A single RotoTranslation or RecursiveRotoTranslation
            return [self.rotoTranslation.to4DMatrix()]
        except AttributeError:
            matrices = [] # Then it is a stack of recursive definitions
            for rtrans in self.rotoTranslation:
                matrices.append(rtrans.to4DMatrix())
            return matrices

    def to4DMatrix(self):
        matrices = []
        matrices.extend(self._expansionsTo4DMatrices())
        matrices.extend(self._translationsTo4DMatrices())
        matrices.extend(self._rotoTranslationsTo4DMatrices())
        return _rightMultiplyMatrices(matrices)


class RotoTranslation(object):
    """translation in mm, angles in degrees"""
    def __init__(self, name, axis=None, polar=0., azimuth=0.,
                 translation=None, flukaregistry=None):
        self.name = name
        self.axis = axis
        self.polar = polar
        self.azimuth = azimuth
        self.translation = translation

        if not axis and any([polar, azimuth]):
            raise TypeError("Axis not set for non-zero polar and/or azimuth.")

        if flukaregistry is not None:
            flukaregistry.addRotoTranslation(self)

        if len(name) > 10:
            raise ValueError(
                "Name {} is too long.  Max length = 10.".format(name))
        if polar < 0 or polar > 180.:
            raise ValueError(
                "Polar angle must be between 0 and +180 deg: {}".format(polar))
        if azimuth < -180. or azimuth > 180.:
            raise ValueError(
                "Azimuth must be between -180 and +180 deg: {}".format(azimuth))
        if translation is None:
            self.translation = Three([0, 0, 0])

    def __repr__(self):
        return "<RotoTranslation: {}>".format(self.name)

    def to4DMatrix(self):
        theta = self.polar * np.pi / 180.
        phi = self.azimuth * np.pi / 180.
        ct = np.cos(theta)
        cp = np.cos(phi)
        st = np.sin(theta)
        sp = np.sin(phi)

        tx, ty, tz = self.translation
        # The sine and cosine terms in the translation column are to make
        # it so the rotation is applied *after* the translation, which is
        # the case in FLUKA.
        if self.axis == "x":
            r1 = np.array([[ ct,  st, 0, 0],
                           [-st,  ct, 0, 0],
                           [  0,   0, 1, 0],
                           [  0,   0, 0, 1]])
            r2 = np.array([[1,   0,  0,            tx],
                           [0,  cp, sp, ty*cp + tz*sp],
                           [0, -sp, cp, tz*cp - ty*sp],
                           [0,   0,  0,             1]])
        elif self.axis == "y":
            r1 = np.array([[1,   0,  0, 0],
                           [0,  ct, st, 0],
                           [0, -st, ct, 0],
                           [0,   0,  0, 1]])
            r2 = np.array([[cp, 0, -sp, tx*cp - tz*sp],
                           [ 0, 1,   0,            ty],
                           [sp, 0,  cp, tx*sp + tz*cp],
                           [ 0, 0,   0,             1]])
        elif self.axis == "z":
            r1 = np.array([[ct, 0, -st, 0],
                           [ 0, 1,   0, 0],
                           [st, 0,  ct, 0],
                           [ 0, 0,   0, 1]])
            r2 = np.array([[ cp, sp, 0, tx*cp + ty*sp],
                           [-sp, cp, 0, ty*cp - tx*sp],
                           [  0,  0, 1,            tz],
                           [  0,  0, 0,             1]])
        else:
            msg = "Unable to determine rotation matrix axis: {}.".format(
                self.axis)
            raise ValueError(msg)

        return r1.dot(r2)

    def toCard(self):
        index = ["z", "x", "y", "z"].index(self.axis)
        index += 10000 # see fluka manual on ROT-DEFI
        tx, ty, tz = self.translation
        # CONVERTING TO CENTIMETRES!!
        return Card("ROT-DEFI", index,
                    self.polar, self.azimuth,
                    tx*0.1, ty*0.1, tz*0.1, self.name)

    def flukaFreeString(self):
        return self.toCard().toFreeString()

    @classmethod
    def fromCard(cls, card):
        if card.keyword != "ROT-DEFI":
            raise ValueError("Not a ROT-DEFI card, keyword={}".format(
                card.keyword))
        card = card.nonesToZero()

        what1 = int(card.what1)
        if what1 >= 1000.:
            # i = what1 // 1000
            j = int(str(what1)[-1])
        elif what1 >= 100. and what1 < 1000.:
            # i = int(str(what1)[-1])
            j = what1 // 100
        elif what1 > 0 and what1 <= 100:
            # i = int(what1)
            j = 0
        elif what1 == 0:
            # If left empty (i.e. 0), then this is a transformation
            # about the z-axis.  But I don't know what that means for i.
            # i = what1
            j = 0
        else:
            raise ValueError(
                "Unable to parse ROT-DEFI WHAT1: {}.".format(what1))

        try:
            axis = ["z", "x", "y", "z"][j] # j = 0, 1, 2, 3
        except IndexError:
            raise FLUKAError(
                "Unable to determine axis for WHAT1={}.".format(what1))

        tx, ty, tz = card.what4, card.what5, card.what6
        # CONVERTING TO MILLIMETRES!!
        tx *= 10
        ty *= 10
        tz *= 10

        return cls(card.sdum, axis, card.what2, card.what3, [tx, ty, tz])


class RecursiveRotoTranslation(MutableSequence):
    """container for dealing with a recursively defined
    rototranslation.  they must also refer to the same rototrans,
    i.e., have the same name.  for a list of rototranslations supplied:

    [a, b, c], the order of evaluation acting on a vector v is
    c*b*a*v.  so teh first rototrans is applied first..  and so on."""
    def __init__(self, name, rotoTranslations):
        self.name = name
        self._rtransList = rotoTranslations

        names = [rtrans.name for rtrans in rotoTranslations]
        for name in names:
            if name != self.name:
                msg = "Appended RotoTranslation does not match name: {}".format(
                    self.name)
                raise ValueError(msg)

    def __repr__(self):
        return "<RecursiveRTrans: {}, {} element(s)>".format(self.name,
                                                             len(self))
    def __getitem__(self, i):
        return self._rtransList[i]

    def _raiseIfDifferentName(self, name):
        if self.name != name:
            msg = ("Inserted RotoTranslation must have same"
                   " name as the RecursiveRotoTranslation.")
            raise ValueError(msg)

    def __setitem__(self, i, obj):
        if not isinstance(obj, RotoTranslation):
            raise TypeError("Items must be RotoTranslation instances")
        self._raiseIfDifferentName(obj.name)
        self._rtransList[i] = obj

    def __delitem__(self, i):
        del self._rtransList[i]

    def __len__(self):
        return len(self._rtransList)

    def insert(self, i, obj):
        if not isinstance(obj, RotoTranslation):
            raise TypeError("Items must be RotoTranslation instances")
        self._raiseIfDifferentName(obj.name)
        self._rtransList.insert(i, obj)

    def to4DMatrix(self):
        matrices = [mat.to4DMatrix() for mat in self]
        return _rightMultiplyMatrices(matrices)

    def flukaFreeString(self):
        return "\n".join([c.toCard().toFreeString() for c in self])


def rotoTranslationFromTBxyz(name, tbxyz, flukaregistry=None):
    """tbxyz = trait bryan angles in radians"""
    # Reverse it's because different convention in FLUKA (passive vs
    # active angles).
    tbxyz = Three(reverse(tbxyz))
    result = RecursiveRotoTranslation(name, [])
    # Don't append a RotoTranslation for 0-angle rotations.
    # Note that we are converting from radians to degrees here.
    if tbxyz.x:
        result.append(RotoTranslation(name, axis="x",
                                      azimuth=tbxyz[0]*180/np.pi,
                                      flukaregistry=flukaregistry))
    if tbxyz.y:
        result.append(RotoTranslation(name, axis="y",
                                      azimuth=tbxyz[1]*180/np.pi,
                                      flukaregistry=flukaregistry))
    if tbxyz.z:
        result.append(RotoTranslation(name, axis="z",
                                      azimuth=tbxyz[2]*180/np.pi,
                                      flukaregistry=flukaregistry))

    return result

def rotoTranslationFromTra2(name, tra2, flukaregistry=None):
    rotation = tra2[0]
    translation = tra2[1]

    # Start with rotation
    result = rotoTranslationFromTBxyz(name, rotation,
                                      flukaregistry=flukaregistry)

    if any(translation): # Don't append a translation of zeros
        result.append(RotoTranslation(name, axis="x",
                                      translation=translation,
                                      flukaregistry=flukaregistry))
    return result

def _translationTo4DMatrix(translation):
    mat = np.identity(4)
    mat[:3, 3] = translation
    return mat

def _expansionFactorTo4DMatrix(factor):
    mat = np.identity(4)
    mat[0, 0] = mat[1, 1] = mat[2, 2] = factor
    return mat

def _rightMultiplyMatrices(matrices):
    # Reverse because we apply the matrices to a vector v in in
    # the order the matrices have been appended, and reduce runs
    # from left to right.  so a list of matrices [A, B, C] applied to
    # a vector v as (C*B*A)*v.
    return reduce(np.matmul, matrices[::-1], np.identity(4))
