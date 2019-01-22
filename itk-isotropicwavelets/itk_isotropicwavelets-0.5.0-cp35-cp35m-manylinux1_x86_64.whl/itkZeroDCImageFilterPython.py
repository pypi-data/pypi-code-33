# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkZeroDCImageFilterPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkZeroDCImageFilterPython', [dirname(__file__)])
        except ImportError:
            import _itkZeroDCImageFilterPython
            return _itkZeroDCImageFilterPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkZeroDCImageFilterPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkZeroDCImageFilterPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkZeroDCImageFilterPython
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


import ITKCommonBasePython
import pyBasePython
import itkImageToImageFilterAPython
import itkImagePython
import itkVectorPython
import vnl_vectorPython
import stdcomplexPython
import vnl_matrixPython
import vnl_vector_refPython
import itkFixedArrayPython
import itkSizePython
import itkImageRegionPython
import itkIndexPython
import itkOffsetPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkPointPython
import itkCovariantVectorPython
import itkSymmetricSecondRankTensorPython
import itkRGBAPixelPython
import itkRGBPixelPython
import itkVectorImagePython
import itkVariableLengthVectorPython
import itkImageSourcePython
import itkImageSourceCommonPython
import itkImageToImageFilterCommonPython

def itkZeroDCImageFilterIF3_New():
  return itkZeroDCImageFilterIF3.New()


def itkZeroDCImageFilterIUS3_New():
  return itkZeroDCImageFilterIUS3.New()


def itkZeroDCImageFilterIUC3_New():
  return itkZeroDCImageFilterIUC3.New()


def itkZeroDCImageFilterISS3_New():
  return itkZeroDCImageFilterISS3.New()


def itkZeroDCImageFilterIF2_New():
  return itkZeroDCImageFilterIF2.New()


def itkZeroDCImageFilterIUS2_New():
  return itkZeroDCImageFilterIUS2.New()


def itkZeroDCImageFilterIUC2_New():
  return itkZeroDCImageFilterIUC2.New()


def itkZeroDCImageFilterISS2_New():
  return itkZeroDCImageFilterISS2.New()

class itkZeroDCImageFilterIF2(itkImageToImageFilterAPython.itkImageToImageFilterIF2IF2):
    """Proxy of C++ itkZeroDCImageFilterIF2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIF2_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIF2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIF2_Pointer":
        """Clone(itkZeroDCImageFilterIF2 self) -> itkZeroDCImageFilterIF2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIF2 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIF2

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIF2 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIF2"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIF2

        Create a new object of the class itkZeroDCImageFilterIF2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIF2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIF2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIF2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIF2.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_Clone, None, itkZeroDCImageFilterIF2)
itkZeroDCImageFilterIF2.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_GetMean, None, itkZeroDCImageFilterIF2)
itkZeroDCImageFilterIF2_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_swigregister
itkZeroDCImageFilterIF2_swigregister(itkZeroDCImageFilterIF2)

def itkZeroDCImageFilterIF2___New_orig__() -> "itkZeroDCImageFilterIF2_Pointer":
    """itkZeroDCImageFilterIF2___New_orig__() -> itkZeroDCImageFilterIF2_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2___New_orig__()

def itkZeroDCImageFilterIF2_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIF2 *":
    """itkZeroDCImageFilterIF2_cast(itkLightObject obj) -> itkZeroDCImageFilterIF2"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF2_cast(obj)

class itkZeroDCImageFilterIF3(itkImageToImageFilterAPython.itkImageToImageFilterIF3IF3):
    """Proxy of C++ itkZeroDCImageFilterIF3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIF3_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIF3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIF3_Pointer":
        """Clone(itkZeroDCImageFilterIF3 self) -> itkZeroDCImageFilterIF3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIF3 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIF3

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIF3 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIF3"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIF3

        Create a new object of the class itkZeroDCImageFilterIF3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIF3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIF3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIF3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIF3.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_Clone, None, itkZeroDCImageFilterIF3)
itkZeroDCImageFilterIF3.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_GetMean, None, itkZeroDCImageFilterIF3)
itkZeroDCImageFilterIF3_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_swigregister
itkZeroDCImageFilterIF3_swigregister(itkZeroDCImageFilterIF3)

def itkZeroDCImageFilterIF3___New_orig__() -> "itkZeroDCImageFilterIF3_Pointer":
    """itkZeroDCImageFilterIF3___New_orig__() -> itkZeroDCImageFilterIF3_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3___New_orig__()

def itkZeroDCImageFilterIF3_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIF3 *":
    """itkZeroDCImageFilterIF3_cast(itkLightObject obj) -> itkZeroDCImageFilterIF3"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIF3_cast(obj)

class itkZeroDCImageFilterISS2(itkImageToImageFilterAPython.itkImageToImageFilterISS2ISS2):
    """Proxy of C++ itkZeroDCImageFilterISS2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterISS2_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterISS2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterISS2_Pointer":
        """Clone(itkZeroDCImageFilterISS2 self) -> itkZeroDCImageFilterISS2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterISS2 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterISS2

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterISS2 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterISS2"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterISS2

        Create a new object of the class itkZeroDCImageFilterISS2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterISS2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterISS2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterISS2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterISS2.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_Clone, None, itkZeroDCImageFilterISS2)
itkZeroDCImageFilterISS2.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_GetMean, None, itkZeroDCImageFilterISS2)
itkZeroDCImageFilterISS2_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_swigregister
itkZeroDCImageFilterISS2_swigregister(itkZeroDCImageFilterISS2)

def itkZeroDCImageFilterISS2___New_orig__() -> "itkZeroDCImageFilterISS2_Pointer":
    """itkZeroDCImageFilterISS2___New_orig__() -> itkZeroDCImageFilterISS2_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2___New_orig__()

def itkZeroDCImageFilterISS2_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterISS2 *":
    """itkZeroDCImageFilterISS2_cast(itkLightObject obj) -> itkZeroDCImageFilterISS2"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS2_cast(obj)

class itkZeroDCImageFilterISS3(itkImageToImageFilterAPython.itkImageToImageFilterISS3ISS3):
    """Proxy of C++ itkZeroDCImageFilterISS3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterISS3_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterISS3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterISS3_Pointer":
        """Clone(itkZeroDCImageFilterISS3 self) -> itkZeroDCImageFilterISS3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterISS3 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterISS3

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterISS3 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterISS3"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterISS3

        Create a new object of the class itkZeroDCImageFilterISS3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterISS3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterISS3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterISS3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterISS3.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_Clone, None, itkZeroDCImageFilterISS3)
itkZeroDCImageFilterISS3.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_GetMean, None, itkZeroDCImageFilterISS3)
itkZeroDCImageFilterISS3_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_swigregister
itkZeroDCImageFilterISS3_swigregister(itkZeroDCImageFilterISS3)

def itkZeroDCImageFilterISS3___New_orig__() -> "itkZeroDCImageFilterISS3_Pointer":
    """itkZeroDCImageFilterISS3___New_orig__() -> itkZeroDCImageFilterISS3_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3___New_orig__()

def itkZeroDCImageFilterISS3_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterISS3 *":
    """itkZeroDCImageFilterISS3_cast(itkLightObject obj) -> itkZeroDCImageFilterISS3"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterISS3_cast(obj)

class itkZeroDCImageFilterIUC2(itkImageToImageFilterAPython.itkImageToImageFilterIUC2IUC2):
    """Proxy of C++ itkZeroDCImageFilterIUC2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIUC2_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIUC2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIUC2_Pointer":
        """Clone(itkZeroDCImageFilterIUC2 self) -> itkZeroDCImageFilterIUC2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIUC2 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIUC2

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUC2 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIUC2"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIUC2

        Create a new object of the class itkZeroDCImageFilterIUC2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIUC2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIUC2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIUC2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIUC2.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_Clone, None, itkZeroDCImageFilterIUC2)
itkZeroDCImageFilterIUC2.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_GetMean, None, itkZeroDCImageFilterIUC2)
itkZeroDCImageFilterIUC2_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_swigregister
itkZeroDCImageFilterIUC2_swigregister(itkZeroDCImageFilterIUC2)

def itkZeroDCImageFilterIUC2___New_orig__() -> "itkZeroDCImageFilterIUC2_Pointer":
    """itkZeroDCImageFilterIUC2___New_orig__() -> itkZeroDCImageFilterIUC2_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2___New_orig__()

def itkZeroDCImageFilterIUC2_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUC2 *":
    """itkZeroDCImageFilterIUC2_cast(itkLightObject obj) -> itkZeroDCImageFilterIUC2"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC2_cast(obj)

class itkZeroDCImageFilterIUC3(itkImageToImageFilterAPython.itkImageToImageFilterIUC3IUC3):
    """Proxy of C++ itkZeroDCImageFilterIUC3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIUC3_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIUC3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIUC3_Pointer":
        """Clone(itkZeroDCImageFilterIUC3 self) -> itkZeroDCImageFilterIUC3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIUC3 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIUC3

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUC3 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIUC3"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIUC3

        Create a new object of the class itkZeroDCImageFilterIUC3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIUC3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIUC3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIUC3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIUC3.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_Clone, None, itkZeroDCImageFilterIUC3)
itkZeroDCImageFilterIUC3.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_GetMean, None, itkZeroDCImageFilterIUC3)
itkZeroDCImageFilterIUC3_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_swigregister
itkZeroDCImageFilterIUC3_swigregister(itkZeroDCImageFilterIUC3)

def itkZeroDCImageFilterIUC3___New_orig__() -> "itkZeroDCImageFilterIUC3_Pointer":
    """itkZeroDCImageFilterIUC3___New_orig__() -> itkZeroDCImageFilterIUC3_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3___New_orig__()

def itkZeroDCImageFilterIUC3_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUC3 *":
    """itkZeroDCImageFilterIUC3_cast(itkLightObject obj) -> itkZeroDCImageFilterIUC3"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUC3_cast(obj)

class itkZeroDCImageFilterIUS2(itkImageToImageFilterAPython.itkImageToImageFilterIUS2IUS2):
    """Proxy of C++ itkZeroDCImageFilterIUS2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIUS2_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIUS2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIUS2_Pointer":
        """Clone(itkZeroDCImageFilterIUS2 self) -> itkZeroDCImageFilterIUS2_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIUS2 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIUS2

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUS2 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIUS2"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIUS2

        Create a new object of the class itkZeroDCImageFilterIUS2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIUS2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIUS2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIUS2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIUS2.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_Clone, None, itkZeroDCImageFilterIUS2)
itkZeroDCImageFilterIUS2.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_GetMean, None, itkZeroDCImageFilterIUS2)
itkZeroDCImageFilterIUS2_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_swigregister
itkZeroDCImageFilterIUS2_swigregister(itkZeroDCImageFilterIUS2)

def itkZeroDCImageFilterIUS2___New_orig__() -> "itkZeroDCImageFilterIUS2_Pointer":
    """itkZeroDCImageFilterIUS2___New_orig__() -> itkZeroDCImageFilterIUS2_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2___New_orig__()

def itkZeroDCImageFilterIUS2_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUS2 *":
    """itkZeroDCImageFilterIUS2_cast(itkLightObject obj) -> itkZeroDCImageFilterIUS2"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS2_cast(obj)

class itkZeroDCImageFilterIUS3(itkImageToImageFilterAPython.itkImageToImageFilterIUS3IUS3):
    """Proxy of C++ itkZeroDCImageFilterIUS3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkZeroDCImageFilterIUS3_Pointer":
        """__New_orig__() -> itkZeroDCImageFilterIUS3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkZeroDCImageFilterIUS3_Pointer":
        """Clone(itkZeroDCImageFilterIUS3 self) -> itkZeroDCImageFilterIUS3_Pointer"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_Clone(self)

    ImageTypeHasNumericTraitsCheck = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_ImageTypeHasNumericTraitsCheck

    def GetMean(self) -> "double":
        """GetMean(itkZeroDCImageFilterIUS3 self) -> double"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_GetMean(self)

    __swig_destroy__ = _itkZeroDCImageFilterPython.delete_itkZeroDCImageFilterIUS3

    def cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUS3 *":
        """cast(itkLightObject obj) -> itkZeroDCImageFilterIUS3"""
        return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkZeroDCImageFilterIUS3

        Create a new object of the class itkZeroDCImageFilterIUS3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkZeroDCImageFilterIUS3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkZeroDCImageFilterIUS3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkZeroDCImageFilterIUS3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkZeroDCImageFilterIUS3.Clone = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_Clone, None, itkZeroDCImageFilterIUS3)
itkZeroDCImageFilterIUS3.GetMean = new_instancemethod(_itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_GetMean, None, itkZeroDCImageFilterIUS3)
itkZeroDCImageFilterIUS3_swigregister = _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_swigregister
itkZeroDCImageFilterIUS3_swigregister(itkZeroDCImageFilterIUS3)

def itkZeroDCImageFilterIUS3___New_orig__() -> "itkZeroDCImageFilterIUS3_Pointer":
    """itkZeroDCImageFilterIUS3___New_orig__() -> itkZeroDCImageFilterIUS3_Pointer"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3___New_orig__()

def itkZeroDCImageFilterIUS3_cast(obj: 'itkLightObject') -> "itkZeroDCImageFilterIUS3 *":
    """itkZeroDCImageFilterIUS3_cast(itkLightObject obj) -> itkZeroDCImageFilterIUS3"""
    return _itkZeroDCImageFilterPython.itkZeroDCImageFilterIUS3_cast(obj)


def zero_dc_image_filter(*args, **kwargs):
    """Procedural interface for ZeroDCImageFilter"""
    import itk
    return itk.ZeroDCImageFilter.__call__(*args, **kwargs)



