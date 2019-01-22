# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkHeldIsotropicWaveletPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkHeldIsotropicWaveletPython', [dirname(__file__)])
        except ImportError:
            import _itkHeldIsotropicWaveletPython
            return _itkHeldIsotropicWaveletPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkHeldIsotropicWaveletPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkHeldIsotropicWaveletPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkHeldIsotropicWaveletPython
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
import itkSpatialFunctionPython
import itkPointPython
import itkVectorPython
import vnl_vectorPython
import stdcomplexPython
import pyBasePython
import vnl_matrixPython
import vnl_vector_refPython
import itkFixedArrayPython
import itkFunctionBasePython
import ITKCommonBasePython
import itkCovariantVectorPython
import itkRGBPixelPython
import itkRGBAPixelPython
import itkArrayPython
import itkContinuousIndexPython
import itkIndexPython
import itkOffsetPython
import itkSizePython
import itkImagePython
import itkImageRegionPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkSymmetricSecondRankTensorPython

def itkHeldIsotropicWaveletF3PD3_New():
  return itkHeldIsotropicWaveletF3PD3.New()


def itkHeldIsotropicWaveletF2PD2_New():
  return itkHeldIsotropicWaveletF2PD2.New()

class itkHeldIsotropicWaveletF2PD2(itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2):
    """Proxy of C++ itkHeldIsotropicWaveletF2PD2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__():
        """__New_orig__() -> itkHeldIsotropicWaveletF2PD2_Pointer"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self):
        """Clone(itkHeldIsotropicWaveletF2PD2 self) -> itkHeldIsotropicWaveletF2PD2_Pointer"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_Clone(self)


    def SetPolynomialOrder(self, _arg):
        """SetPolynomialOrder(itkHeldIsotropicWaveletF2PD2 self, unsigned int const _arg)"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_SetPolynomialOrder(self, _arg)


    def GetPolynomialOrder(self):
        """GetPolynomialOrder(itkHeldIsotropicWaveletF2PD2 self) -> unsigned int"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_GetPolynomialOrder(self)


    def ComputePolynom(self, freq_norm_in_hz, order):
        """ComputePolynom(itkHeldIsotropicWaveletF2PD2 self, float const & freq_norm_in_hz, unsigned int const & order) -> float"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_ComputePolynom(self, freq_norm_in_hz, order)

    __swig_destroy__ = _itkHeldIsotropicWaveletPython.delete_itkHeldIsotropicWaveletF2PD2

    def cast(obj):
        """cast(itkLightObject obj) -> itkHeldIsotropicWaveletF2PD2"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkHeldIsotropicWaveletF2PD2

        Create a new object of the class itkHeldIsotropicWaveletF2PD2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkHeldIsotropicWaveletF2PD2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkHeldIsotropicWaveletF2PD2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkHeldIsotropicWaveletF2PD2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkHeldIsotropicWaveletF2PD2.Clone = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_Clone, None, itkHeldIsotropicWaveletF2PD2)
itkHeldIsotropicWaveletF2PD2.SetPolynomialOrder = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_SetPolynomialOrder, None, itkHeldIsotropicWaveletF2PD2)
itkHeldIsotropicWaveletF2PD2.GetPolynomialOrder = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_GetPolynomialOrder, None, itkHeldIsotropicWaveletF2PD2)
itkHeldIsotropicWaveletF2PD2.ComputePolynom = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_ComputePolynom, None, itkHeldIsotropicWaveletF2PD2)
itkHeldIsotropicWaveletF2PD2_swigregister = _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_swigregister
itkHeldIsotropicWaveletF2PD2_swigregister(itkHeldIsotropicWaveletF2PD2)

def itkHeldIsotropicWaveletF2PD2___New_orig__():
    """itkHeldIsotropicWaveletF2PD2___New_orig__() -> itkHeldIsotropicWaveletF2PD2_Pointer"""
    return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2___New_orig__()

def itkHeldIsotropicWaveletF2PD2_cast(obj):
    """itkHeldIsotropicWaveletF2PD2_cast(itkLightObject obj) -> itkHeldIsotropicWaveletF2PD2"""
    return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF2PD2_cast(obj)

class itkHeldIsotropicWaveletF3PD3(itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3):
    """Proxy of C++ itkHeldIsotropicWaveletF3PD3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__():
        """__New_orig__() -> itkHeldIsotropicWaveletF3PD3_Pointer"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self):
        """Clone(itkHeldIsotropicWaveletF3PD3 self) -> itkHeldIsotropicWaveletF3PD3_Pointer"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_Clone(self)


    def SetPolynomialOrder(self, _arg):
        """SetPolynomialOrder(itkHeldIsotropicWaveletF3PD3 self, unsigned int const _arg)"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_SetPolynomialOrder(self, _arg)


    def GetPolynomialOrder(self):
        """GetPolynomialOrder(itkHeldIsotropicWaveletF3PD3 self) -> unsigned int"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_GetPolynomialOrder(self)


    def ComputePolynom(self, freq_norm_in_hz, order):
        """ComputePolynom(itkHeldIsotropicWaveletF3PD3 self, float const & freq_norm_in_hz, unsigned int const & order) -> float"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_ComputePolynom(self, freq_norm_in_hz, order)

    __swig_destroy__ = _itkHeldIsotropicWaveletPython.delete_itkHeldIsotropicWaveletF3PD3

    def cast(obj):
        """cast(itkLightObject obj) -> itkHeldIsotropicWaveletF3PD3"""
        return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkHeldIsotropicWaveletF3PD3

        Create a new object of the class itkHeldIsotropicWaveletF3PD3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkHeldIsotropicWaveletF3PD3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkHeldIsotropicWaveletF3PD3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkHeldIsotropicWaveletF3PD3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkHeldIsotropicWaveletF3PD3.Clone = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_Clone, None, itkHeldIsotropicWaveletF3PD3)
itkHeldIsotropicWaveletF3PD3.SetPolynomialOrder = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_SetPolynomialOrder, None, itkHeldIsotropicWaveletF3PD3)
itkHeldIsotropicWaveletF3PD3.GetPolynomialOrder = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_GetPolynomialOrder, None, itkHeldIsotropicWaveletF3PD3)
itkHeldIsotropicWaveletF3PD3.ComputePolynom = new_instancemethod(_itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_ComputePolynom, None, itkHeldIsotropicWaveletF3PD3)
itkHeldIsotropicWaveletF3PD3_swigregister = _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_swigregister
itkHeldIsotropicWaveletF3PD3_swigregister(itkHeldIsotropicWaveletF3PD3)

def itkHeldIsotropicWaveletF3PD3___New_orig__():
    """itkHeldIsotropicWaveletF3PD3___New_orig__() -> itkHeldIsotropicWaveletF3PD3_Pointer"""
    return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3___New_orig__()

def itkHeldIsotropicWaveletF3PD3_cast(obj):
    """itkHeldIsotropicWaveletF3PD3_cast(itkLightObject obj) -> itkHeldIsotropicWaveletF3PD3"""
    return _itkHeldIsotropicWaveletPython.itkHeldIsotropicWaveletF3PD3_cast(obj)



