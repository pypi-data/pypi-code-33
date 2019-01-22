# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkIsotropicWaveletFrequencyFunctionPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkIsotropicWaveletFrequencyFunctionPython', [dirname(__file__)])
        except ImportError:
            import _itkIsotropicWaveletFrequencyFunctionPython
            return _itkIsotropicWaveletFrequencyFunctionPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkIsotropicWaveletFrequencyFunctionPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkIsotropicWaveletFrequencyFunctionPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkIsotropicWaveletFrequencyFunctionPython
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

def itkIsotropicWaveletFrequencyFunctionF3PD3_New():
  return itkIsotropicWaveletFrequencyFunctionF3PD3.New()


def itkIsotropicWaveletFrequencyFunctionF2PD2_New():
  return itkIsotropicWaveletFrequencyFunctionF2PD2.New()

class itkIsotropicWaveletFrequencyFunctionF2PD2(itkIsotropicFrequencyFunctionPython.itkIsotropicFrequencyFunctionF2PD2):
    """Proxy of C++ itkIsotropicWaveletFrequencyFunctionF2PD2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr

    def EvaluateForwardLowPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateForwardLowPassFilter(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardLowPassFilter(self, freq_in_hz)


    def EvaluateForwardHighPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateForwardHighPassFilter(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardHighPassFilter(self, freq_in_hz)


    def EvaluateForwardSubBand(self, freq_in_hz: 'float const &', j: 'unsigned int') -> "float":
        """EvaluateForwardSubBand(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz, unsigned int j) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardSubBand(self, freq_in_hz, j)


    def EvaluateInverseLowPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateInverseLowPassFilter(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseLowPassFilter(self, freq_in_hz)


    def EvaluateInverseHighPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateInverseHighPassFilter(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseHighPassFilter(self, freq_in_hz)


    def EvaluateInverseSubBand(self, freq_in_hz: 'float const &', j: 'unsigned int') -> "float":
        """EvaluateInverseSubBand(itkIsotropicWaveletFrequencyFunctionF2PD2 self, float const & freq_in_hz, unsigned int j) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseSubBand(self, freq_in_hz, j)


    def GetHighPassSubBands(self) -> "unsigned int":
        """GetHighPassSubBands(itkIsotropicWaveletFrequencyFunctionF2PD2 self) -> unsigned int"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_GetHighPassSubBands(self)


    def SetHighPassSubBands(self, high_pass_bands: 'unsigned int const &') -> "void":
        """SetHighPassSubBands(itkIsotropicWaveletFrequencyFunctionF2PD2 self, unsigned int const & high_pass_bands)"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_SetHighPassSubBands(self, high_pass_bands)


    def GetFreqCutOff(self) -> "float":
        """GetFreqCutOff(itkIsotropicWaveletFrequencyFunctionF2PD2 self) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_GetFreqCutOff(self)

    __swig_destroy__ = _itkIsotropicWaveletFrequencyFunctionPython.delete_itkIsotropicWaveletFrequencyFunctionF2PD2

    def cast(obj: 'itkLightObject') -> "itkIsotropicWaveletFrequencyFunctionF2PD2 *":
        """cast(itkLightObject obj) -> itkIsotropicWaveletFrequencyFunctionF2PD2"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkIsotropicWaveletFrequencyFunctionF2PD2

        Create a new object of the class itkIsotropicWaveletFrequencyFunctionF2PD2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkIsotropicWaveletFrequencyFunctionF2PD2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkIsotropicWaveletFrequencyFunctionF2PD2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkIsotropicWaveletFrequencyFunctionF2PD2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateForwardLowPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardLowPassFilter, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateForwardHighPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardHighPassFilter, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateForwardSubBand = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateForwardSubBand, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateInverseLowPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseLowPassFilter, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateInverseHighPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseHighPassFilter, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.EvaluateInverseSubBand = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_EvaluateInverseSubBand, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.GetHighPassSubBands = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_GetHighPassSubBands, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.SetHighPassSubBands = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_SetHighPassSubBands, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2.GetFreqCutOff = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_GetFreqCutOff, None, itkIsotropicWaveletFrequencyFunctionF2PD2)
itkIsotropicWaveletFrequencyFunctionF2PD2_swigregister = _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_swigregister
itkIsotropicWaveletFrequencyFunctionF2PD2_swigregister(itkIsotropicWaveletFrequencyFunctionF2PD2)

def itkIsotropicWaveletFrequencyFunctionF2PD2_cast(obj: 'itkLightObject') -> "itkIsotropicWaveletFrequencyFunctionF2PD2 *":
    """itkIsotropicWaveletFrequencyFunctionF2PD2_cast(itkLightObject obj) -> itkIsotropicWaveletFrequencyFunctionF2PD2"""
    return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF2PD2_cast(obj)

class itkIsotropicWaveletFrequencyFunctionF3PD3(itkIsotropicFrequencyFunctionPython.itkIsotropicFrequencyFunctionF3PD3):
    """Proxy of C++ itkIsotropicWaveletFrequencyFunctionF3PD3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined - class is abstract")
    __repr__ = _swig_repr

    def EvaluateForwardLowPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateForwardLowPassFilter(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardLowPassFilter(self, freq_in_hz)


    def EvaluateForwardHighPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateForwardHighPassFilter(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardHighPassFilter(self, freq_in_hz)


    def EvaluateForwardSubBand(self, freq_in_hz: 'float const &', j: 'unsigned int') -> "float":
        """EvaluateForwardSubBand(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz, unsigned int j) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardSubBand(self, freq_in_hz, j)


    def EvaluateInverseLowPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateInverseLowPassFilter(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseLowPassFilter(self, freq_in_hz)


    def EvaluateInverseHighPassFilter(self, freq_in_hz: 'float const &') -> "float":
        """EvaluateInverseHighPassFilter(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseHighPassFilter(self, freq_in_hz)


    def EvaluateInverseSubBand(self, freq_in_hz: 'float const &', j: 'unsigned int') -> "float":
        """EvaluateInverseSubBand(itkIsotropicWaveletFrequencyFunctionF3PD3 self, float const & freq_in_hz, unsigned int j) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseSubBand(self, freq_in_hz, j)


    def GetHighPassSubBands(self) -> "unsigned int":
        """GetHighPassSubBands(itkIsotropicWaveletFrequencyFunctionF3PD3 self) -> unsigned int"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_GetHighPassSubBands(self)


    def SetHighPassSubBands(self, high_pass_bands: 'unsigned int const &') -> "void":
        """SetHighPassSubBands(itkIsotropicWaveletFrequencyFunctionF3PD3 self, unsigned int const & high_pass_bands)"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_SetHighPassSubBands(self, high_pass_bands)


    def GetFreqCutOff(self) -> "float":
        """GetFreqCutOff(itkIsotropicWaveletFrequencyFunctionF3PD3 self) -> float"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_GetFreqCutOff(self)

    __swig_destroy__ = _itkIsotropicWaveletFrequencyFunctionPython.delete_itkIsotropicWaveletFrequencyFunctionF3PD3

    def cast(obj: 'itkLightObject') -> "itkIsotropicWaveletFrequencyFunctionF3PD3 *":
        """cast(itkLightObject obj) -> itkIsotropicWaveletFrequencyFunctionF3PD3"""
        return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkIsotropicWaveletFrequencyFunctionF3PD3

        Create a new object of the class itkIsotropicWaveletFrequencyFunctionF3PD3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkIsotropicWaveletFrequencyFunctionF3PD3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkIsotropicWaveletFrequencyFunctionF3PD3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkIsotropicWaveletFrequencyFunctionF3PD3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateForwardLowPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardLowPassFilter, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateForwardHighPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardHighPassFilter, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateForwardSubBand = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateForwardSubBand, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateInverseLowPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseLowPassFilter, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateInverseHighPassFilter = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseHighPassFilter, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.EvaluateInverseSubBand = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_EvaluateInverseSubBand, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.GetHighPassSubBands = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_GetHighPassSubBands, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.SetHighPassSubBands = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_SetHighPassSubBands, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3.GetFreqCutOff = new_instancemethod(_itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_GetFreqCutOff, None, itkIsotropicWaveletFrequencyFunctionF3PD3)
itkIsotropicWaveletFrequencyFunctionF3PD3_swigregister = _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_swigregister
itkIsotropicWaveletFrequencyFunctionF3PD3_swigregister(itkIsotropicWaveletFrequencyFunctionF3PD3)

def itkIsotropicWaveletFrequencyFunctionF3PD3_cast(obj: 'itkLightObject') -> "itkIsotropicWaveletFrequencyFunctionF3PD3 *":
    """itkIsotropicWaveletFrequencyFunctionF3PD3_cast(itkLightObject obj) -> itkIsotropicWaveletFrequencyFunctionF3PD3"""
    return _itkIsotropicWaveletFrequencyFunctionPython.itkIsotropicWaveletFrequencyFunctionF3PD3_cast(obj)



