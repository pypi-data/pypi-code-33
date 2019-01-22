# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkSimoncelliIsotropicWaveletPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkSimoncelliIsotropicWaveletPython', [dirname(__file__)])
        except ImportError:
            import _itkSimoncelliIsotropicWaveletPython
            return _itkSimoncelliIsotropicWaveletPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkSimoncelliIsotropicWaveletPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkSimoncelliIsotropicWaveletPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkSimoncelliIsotropicWaveletPython
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        object.__setattr__(self, name, value)
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0



def _swig_setattr_nondynamic_method(set):
    def set_attr(self, name, value):
        if (name == "thisown"):
            return self.this.own(value)
        if hasattr(self, name) or (name == "this"):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


import itkIsotropicWaveletFrequencyFunctionPython
import itkIsotropicFrequencyFunctionPython
import itkFrequencyFunctionPython
import itkPointPython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython
import pyBasePython
import vnl_vector_refPython
import itkFixedArrayPython
import itkVectorPython
import itkSpatialFunctionPython
import ITKCommonBasePython
import itkFunctionBasePython
import itkArrayPython
import itkRGBAPixelPython
import itkContinuousIndexPython
import itkIndexPython
import itkOffsetPython
import itkSizePython
import itkRGBPixelPython
import itkCovariantVectorPython
import itkImagePython
import itkSymmetricSecondRankTensorPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkImageRegionPython

def itkSimoncelliIsotropicWaveletF3PD3_New():
  return itkSimoncelliIsotropicWaveletF3PD3.New()


def itkSimoncelliIsotropicWaveletF2PD2_New():
  return itkSimoncelliIsotropicWaveletF2PD2.New()

class itkSimoncelliIsotropicWaveletF2PD2(itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2):
    """Proxy of C++ itkSimoncelliIsotropicWaveletF2PD2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSimoncelliIsotropicWaveletF2PD2_Pointer":
        """__New_orig__() -> itkSimoncelliIsotropicWaveletF2PD2_Pointer"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkSimoncelliIsotropicWaveletF2PD2_Pointer":
        """Clone(itkSimoncelliIsotropicWaveletF2PD2 self) -> itkSimoncelliIsotropicWaveletF2PD2_Pointer"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2_Clone(self)

    __swig_destroy__ = _itkSimoncelliIsotropicWaveletPython.delete_itkSimoncelliIsotropicWaveletF2PD2

    def cast(obj: 'itkLightObject') -> "itkSimoncelliIsotropicWaveletF2PD2 *":
        """cast(itkLightObject obj) -> itkSimoncelliIsotropicWaveletF2PD2"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkSimoncelliIsotropicWaveletF2PD2

        Create a new object of the class itkSimoncelliIsotropicWaveletF2PD2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSimoncelliIsotropicWaveletF2PD2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSimoncelliIsotropicWaveletF2PD2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSimoncelliIsotropicWaveletF2PD2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSimoncelliIsotropicWaveletF2PD2.Clone = new_instancemethod(_itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2_Clone, None, itkSimoncelliIsotropicWaveletF2PD2)
itkSimoncelliIsotropicWaveletF2PD2_swigregister = _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2_swigregister
itkSimoncelliIsotropicWaveletF2PD2_swigregister(itkSimoncelliIsotropicWaveletF2PD2)

def itkSimoncelliIsotropicWaveletF2PD2___New_orig__() -> "itkSimoncelliIsotropicWaveletF2PD2_Pointer":
    """itkSimoncelliIsotropicWaveletF2PD2___New_orig__() -> itkSimoncelliIsotropicWaveletF2PD2_Pointer"""
    return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2___New_orig__()

def itkSimoncelliIsotropicWaveletF2PD2_cast(obj: 'itkLightObject') -> "itkSimoncelliIsotropicWaveletF2PD2 *":
    """itkSimoncelliIsotropicWaveletF2PD2_cast(itkLightObject obj) -> itkSimoncelliIsotropicWaveletF2PD2"""
    return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF2PD2_cast(obj)

class itkSimoncelliIsotropicWaveletF3PD3(itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3):
    """Proxy of C++ itkSimoncelliIsotropicWaveletF3PD3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkSimoncelliIsotropicWaveletF3PD3_Pointer":
        """__New_orig__() -> itkSimoncelliIsotropicWaveletF3PD3_Pointer"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkSimoncelliIsotropicWaveletF3PD3_Pointer":
        """Clone(itkSimoncelliIsotropicWaveletF3PD3 self) -> itkSimoncelliIsotropicWaveletF3PD3_Pointer"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3_Clone(self)

    __swig_destroy__ = _itkSimoncelliIsotropicWaveletPython.delete_itkSimoncelliIsotropicWaveletF3PD3

    def cast(obj: 'itkLightObject') -> "itkSimoncelliIsotropicWaveletF3PD3 *":
        """cast(itkLightObject obj) -> itkSimoncelliIsotropicWaveletF3PD3"""
        return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkSimoncelliIsotropicWaveletF3PD3

        Create a new object of the class itkSimoncelliIsotropicWaveletF3PD3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkSimoncelliIsotropicWaveletF3PD3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkSimoncelliIsotropicWaveletF3PD3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkSimoncelliIsotropicWaveletF3PD3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkSimoncelliIsotropicWaveletF3PD3.Clone = new_instancemethod(_itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3_Clone, None, itkSimoncelliIsotropicWaveletF3PD3)
itkSimoncelliIsotropicWaveletF3PD3_swigregister = _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3_swigregister
itkSimoncelliIsotropicWaveletF3PD3_swigregister(itkSimoncelliIsotropicWaveletF3PD3)

def itkSimoncelliIsotropicWaveletF3PD3___New_orig__() -> "itkSimoncelliIsotropicWaveletF3PD3_Pointer":
    """itkSimoncelliIsotropicWaveletF3PD3___New_orig__() -> itkSimoncelliIsotropicWaveletF3PD3_Pointer"""
    return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3___New_orig__()

def itkSimoncelliIsotropicWaveletF3PD3_cast(obj: 'itkLightObject') -> "itkSimoncelliIsotropicWaveletF3PD3 *":
    """itkSimoncelliIsotropicWaveletF3PD3_cast(itkLightObject obj) -> itkSimoncelliIsotropicWaveletF3PD3"""
    return _itkSimoncelliIsotropicWaveletPython.itkSimoncelliIsotropicWaveletF3PD3_cast(obj)



