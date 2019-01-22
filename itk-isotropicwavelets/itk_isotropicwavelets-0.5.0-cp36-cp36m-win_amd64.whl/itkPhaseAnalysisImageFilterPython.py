# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkPhaseAnalysisImageFilterPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkPhaseAnalysisImageFilterPython', [dirname(__file__)])
        except ImportError:
            import _itkPhaseAnalysisImageFilterPython
            return _itkPhaseAnalysisImageFilterPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkPhaseAnalysisImageFilterPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkPhaseAnalysisImageFilterPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkPhaseAnalysisImageFilterPython
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


import itkImageRegionPython
import itkSizePython
import pyBasePython
import ITKCommonBasePython
import itkIndexPython
import itkOffsetPython
import itkImagePython
import itkRGBPixelPython
import itkFixedArrayPython
import itkSymmetricSecondRankTensorPython
import itkMatrixPython
import itkCovariantVectorPython
import vnl_vector_refPython
import stdcomplexPython
import vnl_vectorPython
import vnl_matrixPython
import itkVectorPython
import itkPointPython
import vnl_matrix_fixedPython
import itkRGBAPixelPython
import itkVariableLengthVectorPython
import itkImageToImageFilterBPython
import itkImageToImageFilterCommonPython
import itkVectorImagePython
import itkImageSourcePython
import itkImageSourceCommonPython

def itkPhaseAnalysisImageFilterVIF3IF3_New():
  return itkPhaseAnalysisImageFilterVIF3IF3.New()


def itkPhaseAnalysisImageFilterVIF2IF2_New():
  return itkPhaseAnalysisImageFilterVIF2IF2.New()

class itkPhaseAnalysisImageFilterVIF2IF2(itkImageToImageFilterBPython.itkImageToImageFilterVIF2IF2):
    """Proxy of C++ itkPhaseAnalysisImageFilterVIF2IF2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkPhaseAnalysisImageFilterVIF2IF2_Pointer":
        """__New_orig__() -> itkPhaseAnalysisImageFilterVIF2IF2_Pointer"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkPhaseAnalysisImageFilterVIF2IF2_Pointer":
        """Clone(itkPhaseAnalysisImageFilterVIF2IF2 self) -> itkPhaseAnalysisImageFilterVIF2IF2_Pointer"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_Clone(self)

    OutputPixelTypeIsFloatCheck = _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_OutputPixelTypeIsFloatCheck

    def GetOutputPhase(self, *args) -> "itkImageF2 *":
        """
        GetOutputPhase(itkPhaseAnalysisImageFilterVIF2IF2 self) -> itkImageF2
        GetOutputPhase(itkPhaseAnalysisImageFilterVIF2IF2 self) -> itkImageF2
        """
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_GetOutputPhase(self, *args)


    def GetOutputAmplitude(self) -> "itkImageF2 *":
        """GetOutputAmplitude(itkPhaseAnalysisImageFilterVIF2IF2 self) -> itkImageF2"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_GetOutputAmplitude(self)

    __swig_destroy__ = _itkPhaseAnalysisImageFilterPython.delete_itkPhaseAnalysisImageFilterVIF2IF2

    def cast(obj: 'itkLightObject') -> "itkPhaseAnalysisImageFilterVIF2IF2 *":
        """cast(itkLightObject obj) -> itkPhaseAnalysisImageFilterVIF2IF2"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkPhaseAnalysisImageFilterVIF2IF2

        Create a new object of the class itkPhaseAnalysisImageFilterVIF2IF2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkPhaseAnalysisImageFilterVIF2IF2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkPhaseAnalysisImageFilterVIF2IF2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkPhaseAnalysisImageFilterVIF2IF2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkPhaseAnalysisImageFilterVIF2IF2.Clone = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_Clone, None, itkPhaseAnalysisImageFilterVIF2IF2)
itkPhaseAnalysisImageFilterVIF2IF2.GetOutputPhase = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_GetOutputPhase, None, itkPhaseAnalysisImageFilterVIF2IF2)
itkPhaseAnalysisImageFilterVIF2IF2.GetOutputAmplitude = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_GetOutputAmplitude, None, itkPhaseAnalysisImageFilterVIF2IF2)
itkPhaseAnalysisImageFilterVIF2IF2_swigregister = _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_swigregister
itkPhaseAnalysisImageFilterVIF2IF2_swigregister(itkPhaseAnalysisImageFilterVIF2IF2)

def itkPhaseAnalysisImageFilterVIF2IF2___New_orig__() -> "itkPhaseAnalysisImageFilterVIF2IF2_Pointer":
    """itkPhaseAnalysisImageFilterVIF2IF2___New_orig__() -> itkPhaseAnalysisImageFilterVIF2IF2_Pointer"""
    return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2___New_orig__()

def itkPhaseAnalysisImageFilterVIF2IF2_cast(obj: 'itkLightObject') -> "itkPhaseAnalysisImageFilterVIF2IF2 *":
    """itkPhaseAnalysisImageFilterVIF2IF2_cast(itkLightObject obj) -> itkPhaseAnalysisImageFilterVIF2IF2"""
    return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF2IF2_cast(obj)

class itkPhaseAnalysisImageFilterVIF3IF3(itkImageToImageFilterBPython.itkImageToImageFilterVIF3IF3):
    """Proxy of C++ itkPhaseAnalysisImageFilterVIF3IF3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkPhaseAnalysisImageFilterVIF3IF3_Pointer":
        """__New_orig__() -> itkPhaseAnalysisImageFilterVIF3IF3_Pointer"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkPhaseAnalysisImageFilterVIF3IF3_Pointer":
        """Clone(itkPhaseAnalysisImageFilterVIF3IF3 self) -> itkPhaseAnalysisImageFilterVIF3IF3_Pointer"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_Clone(self)

    OutputPixelTypeIsFloatCheck = _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_OutputPixelTypeIsFloatCheck

    def GetOutputPhase(self, *args) -> "itkImageF3 *":
        """
        GetOutputPhase(itkPhaseAnalysisImageFilterVIF3IF3 self) -> itkImageF3
        GetOutputPhase(itkPhaseAnalysisImageFilterVIF3IF3 self) -> itkImageF3
        """
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_GetOutputPhase(self, *args)


    def GetOutputAmplitude(self) -> "itkImageF3 *":
        """GetOutputAmplitude(itkPhaseAnalysisImageFilterVIF3IF3 self) -> itkImageF3"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_GetOutputAmplitude(self)

    __swig_destroy__ = _itkPhaseAnalysisImageFilterPython.delete_itkPhaseAnalysisImageFilterVIF3IF3

    def cast(obj: 'itkLightObject') -> "itkPhaseAnalysisImageFilterVIF3IF3 *":
        """cast(itkLightObject obj) -> itkPhaseAnalysisImageFilterVIF3IF3"""
        return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkPhaseAnalysisImageFilterVIF3IF3

        Create a new object of the class itkPhaseAnalysisImageFilterVIF3IF3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkPhaseAnalysisImageFilterVIF3IF3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkPhaseAnalysisImageFilterVIF3IF3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkPhaseAnalysisImageFilterVIF3IF3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkPhaseAnalysisImageFilterVIF3IF3.Clone = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_Clone, None, itkPhaseAnalysisImageFilterVIF3IF3)
itkPhaseAnalysisImageFilterVIF3IF3.GetOutputPhase = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_GetOutputPhase, None, itkPhaseAnalysisImageFilterVIF3IF3)
itkPhaseAnalysisImageFilterVIF3IF3.GetOutputAmplitude = new_instancemethod(_itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_GetOutputAmplitude, None, itkPhaseAnalysisImageFilterVIF3IF3)
itkPhaseAnalysisImageFilterVIF3IF3_swigregister = _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_swigregister
itkPhaseAnalysisImageFilterVIF3IF3_swigregister(itkPhaseAnalysisImageFilterVIF3IF3)

def itkPhaseAnalysisImageFilterVIF3IF3___New_orig__() -> "itkPhaseAnalysisImageFilterVIF3IF3_Pointer":
    """itkPhaseAnalysisImageFilterVIF3IF3___New_orig__() -> itkPhaseAnalysisImageFilterVIF3IF3_Pointer"""
    return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3___New_orig__()

def itkPhaseAnalysisImageFilterVIF3IF3_cast(obj: 'itkLightObject') -> "itkPhaseAnalysisImageFilterVIF3IF3 *":
    """itkPhaseAnalysisImageFilterVIF3IF3_cast(itkLightObject obj) -> itkPhaseAnalysisImageFilterVIF3IF3"""
    return _itkPhaseAnalysisImageFilterPython.itkPhaseAnalysisImageFilterVIF3IF3_cast(obj)


def phase_analysis_image_filter(*args, **kwargs):
    """Procedural interface for PhaseAnalysisImageFilter"""
    import itk
    return itk.PhaseAnalysisImageFilter.__call__(*args, **kwargs)



