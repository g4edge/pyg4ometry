from functools import reduce
from collections.abc import MutableSequence
import numbers
from operator import mul

import numpy as np

from pyg4ometry.transformation import reverse
from pyg4ometry.exceptions import FLUKAError
from .vector import Three
from .card import Card


class MatrixConvertibleMixin:
    def toScaleMatrix(self):
        mtra = self.to4DMatrix()
        result = np.identity(4)
        result[0, 0] = np.linalg.norm(mtra[:,0])
        result[1, 1] = np.linalg.norm(mtra[:,1])
        result[2, 2] = np.linalg.norm(mtra[:,2])
        return result

    def toTranslationMatrix(self):
        mtra = self.to4DMatrix()
        result = np.identity(4)
        result[:3, 3] = mtra[:3, 3]
        return result

    def toRotationMatrix(self):
        mtra = self.to4DMatrix()
        mtra[:3, 3]  = 0.0
        scale = self.toScaleMatrix()
        mtra[:, 2] /= scale[2, 2]
        mtra[:, 1] /= scale[1, 1]
        mtra[:, 0] /= scale[0, 0]
        return mtra

    def netTranslation(self):
        return self.to4DMatrix()[0:,3][:3]

    def netExpansion(self):
        factors = np.diagonal(self.toScaleMatrix())[:3]
        assert np.isclose(factors[0], factors).all()
        return factors[0]

    def leftMultiplyVector(self, vector):
        vector4d = [*vector, 1] # [x, y, z, 1]
        matrix = self.to4DMatrix()
        return Three(matrix.dot(vector4d)[0:3])

    def leftMultiplyRotation(self, matrix):
        return self.toRotationMatrix()[:3, :3] @ matrix


class Transform(MatrixConvertibleMixin):
    """expansion, translation, rotoTranslation can be either a single
    instance of RotoTranslation or a multiple instances of
    RotoTranslation and RecursiveRotoTranslation"""
    def __init__(self, *, expansion=None, translation=None,
                 rotoTranslation=None, invertRotoTranslation=None):
        self.expansion = expansion
        self.translation = translation
        self.rotoTranslation = rotoTranslation
        self.invertRotoTranslation = invertRotoTranslation

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
            return [_translationTo4DMatrix(self.translation)]
        # Then it's a list of translations
        return [_translationTo4DMatrix(m) for m in self.translation]

    def _rotoTranslationsTo4DMatrices(self):
        if not self.rotoTranslation:
            return [np.identity(4)]
        try: # A single RotoTranslation or RecursiveRotoTranslation
            matrix = self.rotoTranslation.to4DMatrix()
            try:
                invertThis = self.invertRotoTranslation[0]
            except (IndexError, TypeError):
                invertThis = bool(self.invertRotoTranslation)
            if invertThis:
                matrix = np.linalg.inv(matrix)
            return [matrix]
        except AttributeError:
            matrices = [] # Then it is a stack of recursive definitions
            anyInversion = bool(self.invertRotoTranslation)
            for i, rtrans in enumerate(self.rotoTranslation):
                matrix = rtrans.to4DMatrix()
                if anyInversion:
                    try:
                        invertThis = self.invertRotoTranslation[i]
                    except (IndexError, AttributeError):
                        msg = "malformed invertRotoTranslation stack."
                        raise ValueError(msg)
                    if invertThis:
                        matrix = np.linalg.inv(matrix)

                matrices.append(matrix)

            return matrices

    def to4DMatrix(self):
        matrices = []
        matrices.extend(self._expansionsTo4DMatrices())
        matrices.extend(self._translationsTo4DMatrices())
        matrices.extend(self._rotoTranslationsTo4DMatrices())
        return _rightMultiplyMatrices(matrices)


class RotoTranslation(MatrixConvertibleMixin):
    """translation in mm, angles in degrees"""
    def __init__(self, name, axis=None, polar=0., azimuth=0.,
                 translation=None, transformationIndex=None, flukaregistry=None):
        self.name = name
        self.axis = axis
        self.polar = polar
        self.azimuth = azimuth
        self.translation = translation
        self.transformationIndex = transformationIndex

        if not axis and any([polar, azimuth]):
            raise TypeError("Axis not set for non-zero polar and/or azimuth.")

        if flukaregistry is not None:
            flukaregistry.addRotoTranslation(self)

        if len(name) > 10:
            raise ValueError(f"Name {name} is too long.  Max length = 10.")
        if polar < 0 or polar > 180.:
            raise ValueError( f"Polar must be between 0 and +180°: {polar}")
        if azimuth < -180. or azimuth > 180.:
            raise ValueError(f"Azimuth must be between ±180°: {azimuth}")
        if translation is None:
            self.translation = Three([0, 0, 0])

    def __repr__(self):
        strs = [f"<RTrans: {self.name}",
                f"t={self.translation}" if self.hasTranslation() else "",
                f"ax={self.axis}" if self.hasRotation() else "",
                f"theta={self.polar}°" if self.polar else "",
                f"phi={self.azimuth}°" if self.hasTranslation else ""]
        strs = [s for s in strs if s]
        result = ", ".join(strs)
        return result + ">"


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
        if self.axis is None:
            r1 = np.identity(4)
            r2 = _translationTo4DMatrix(self.translation)
        elif self.axis == "x":
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
            msg = f"Unable to determine rotation matrix axis: {self.axis}."
            raise ValueError(msg)

        return r1 @ r2

    def toCard(self):
        index = [None, "x", "y", "z"].index(self.axis)
        try:
            index += self.transformationIndex # see fluka manual on ROT-DEFI
        except:
            pass
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
            raise ValueError(f"Unable to parse ROT-DEFI WHAT1: {what1}.")

        try:
            axis = ["z", "x", "y", "z"][j] # j = 0, 1, 2, 3
        except IndexError:
            raise FLUKAError(f"Unable to determine axis for WHAT1={what1}.")

        tx, ty, tz = card.what4, card.what5, card.what6
        # CONVERTING TO MILLIMETRES!!
        tx *= 10
        ty *= 10
        tz *= 10

        return cls(card.sdum, axis, card.what2, card.what3, [tx, ty, tz])

    def hasTranslation(self):
        return any(self.translation)

    def hasRotation(self):
        return self.polar or self.azimuth

    def isPureTranslation(self):
        return (self.polar == 0) and (self.azimuth == 0)


class RecursiveRotoTranslation(MutableSequence, MatrixConvertibleMixin):
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
                msg = f"RotoTranslation doesn't match name: {self.name}"
                raise ValueError(msg)

    def __repr__(self):
        return f"<RecursiveRTrans: {self.name}, {len(self)} element(s)>"

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

    def _transformationIndices(self):
        return [rtrans.index for rtrans in self]

    def areAllTheSameTransformationIndices(self):
        if not self:
            return True
        indices = self._transformationIndices()
        return indices.count(indices[0]) == len(indices)

    @property
    def transformationIndex(self):
        if not self: # if empty
            return None
        return self[0].transformationIndex

    @transformationIndex.setter
    def transformationIndex(self, transformationIndex):
        for rtrans in self:
            rtrans.transformationIndex = transformationIndex

    @transformationIndex.deleter
    def transformationIndex(self):
        for rtrans in self:
            del rtrans.transformationIndex

def rotoTranslationFromTBxyz(name, tbxyz, flukaregistry=None):
    """tbxyz = trait bryan angles in radians"""
    # Reverse it's because different convention in FLUKA (passive vs
    # active angles).
    tbxyz = Three(tbxyz)
    result = RecursiveRotoTranslation(name, [])
    # Don't append a RotoTranslation for 0-angle rotations.
    # Note that we are converting from radians to degrees here.

    if tbxyz.x:
        result.append(RotoTranslation(name, axis="x",
                                      azimuth=-tbxyz[0]*180/np.pi,
                                      flukaregistry=flukaregistry))

    if tbxyz.y:
        result.append(RotoTranslation(name, axis="y",
                                      azimuth=-tbxyz[1]*180/np.pi,
                                      flukaregistry=flukaregistry))

    if tbxyz.z:
        result.append(RotoTranslation(name, axis="z",
                                      azimuth=-tbxyz[2]*180/np.pi,
                                      flukaregistry=flukaregistry))

    return result

def rotoTranslationFromTra2(name, tra2, flukaregistry=None):
    rotation = tra2[0]
    translation = tra2[1]

    # Start with rotation
    result = rotoTranslationFromTBxyz(name, rotation,
                                      flukaregistry=flukaregistry)

    if any(translation): # Don't append a translation of zeros
        result.append(RotoTranslation(name,
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
