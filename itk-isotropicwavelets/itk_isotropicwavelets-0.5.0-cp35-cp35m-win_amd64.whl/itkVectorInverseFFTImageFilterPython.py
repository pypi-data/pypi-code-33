# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkVectorInverseFFTImageFilterPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkVectorInverseFFTImageFilterPython', [dirname(__file__)])
        except ImportError:
            import _itkVectorInverseFFTImageFilterPython
            return _itkVectorInverseFFTImageFilterPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkVectorInverseFFTImageFilterPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkVectorInverseFFTImageFilterPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkVectorInverseFFTImageFilterPython
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
import itkImageSourcePython
import itkImagePython
import itkRGBAPixelPython
import itkFixedArrayPython
import itkMatrixPython
import vnl_vectorPython
import vnl_matrixPython
import stdcomplexPython
import itkPointPython
import vnl_vector_refPython
import itkVectorPython
import itkCovariantVectorPython
import vnl_matrix_fixedPython
import itkSymmetricSecondRankTensorPython
import itkRGBPixelPython
import itkVectorImagePython
import itkVariableLengthVectorPython
import itkImageSourceCommonPython
import itkImageToImageFilterCommonPython

def itkVectorInverseFFTImageFilterVICF3VIF3_New():
  return itkVectorInverseFFTImageFilterVICF3VIF3.New()


def itkVectorInverseFFTImageFilterVICF2VIF2_New():
  return itkVectorInverseFFTImageFilterVICF2VIF2.New()


def itkImageToImageFilterVICF3VIF3_New():
  return itkImageToImageFilterVICF3VIF3.New()


def itkImageToImageFilterVICF2VIF2_New():
  return itkImageToImageFilterVICF2VIF2.New()

class itkImageToImageFilterVICF2VIF2(itkImageSourcePython.itkImageSourceVIF2):
    """Proxy of C++ itkImageToImageFilterVICF2VIF2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def SetInput(self, *args) -> "void":
        """
        SetInput(itkImageToImageFilterVICF2VIF2 self, itkVectorImageCF2 image)
        SetInput(itkImageToImageFilterVICF2VIF2 self, unsigned int arg0, itkVectorImageCF2 image)
        """
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetInput(self, *args)


    def GetInput(self, *args) -> "itkVectorImageCF2 const *":
        """
        GetInput(itkImageToImageFilterVICF2VIF2 self) -> itkVectorImageCF2
        GetInput(itkImageToImageFilterVICF2VIF2 self, unsigned int idx) -> itkVectorImageCF2
        """
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetInput(self, *args)


    def PushBackInput(self, image: 'itkVectorImageCF2') -> "void":
        """PushBackInput(itkImageToImageFilterVICF2VIF2 self, itkVectorImageCF2 image)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PushBackInput(self, image)


    def PopBackInput(self) -> "void":
        """PopBackInput(itkImageToImageFilterVICF2VIF2 self)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PopBackInput(self)


    def PushFrontInput(self, image: 'itkVectorImageCF2') -> "void":
        """PushFrontInput(itkImageToImageFilterVICF2VIF2 self, itkVectorImageCF2 image)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PushFrontInput(self, image)


    def PopFrontInput(self) -> "void":
        """PopFrontInput(itkImageToImageFilterVICF2VIF2 self)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PopFrontInput(self)


    def SetCoordinateTolerance(self, _arg: 'double const') -> "void":
        """SetCoordinateTolerance(itkImageToImageFilterVICF2VIF2 self, double const _arg)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetCoordinateTolerance(self, _arg)


    def GetCoordinateTolerance(self) -> "double":
        """GetCoordinateTolerance(itkImageToImageFilterVICF2VIF2 self) -> double"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetCoordinateTolerance(self)


    def SetDirectionTolerance(self, _arg: 'double const') -> "void":
        """SetDirectionTolerance(itkImageToImageFilterVICF2VIF2 self, double const _arg)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetDirectionTolerance(self, _arg)


    def GetDirectionTolerance(self) -> "double":
        """GetDirectionTolerance(itkImageToImageFilterVICF2VIF2 self) -> double"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetDirectionTolerance(self)

    __swig_destroy__ = _itkVectorInverseFFTImageFilterPython.delete_itkImageToImageFilterVICF2VIF2

    def cast(obj: 'itkLightObject') -> "itkImageToImageFilterVICF2VIF2 *":
        """cast(itkLightObject obj) -> itkImageToImageFilterVICF2VIF2"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkImageToImageFilterVICF2VIF2

        Create a new object of the class itkImageToImageFilterVICF2VIF2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkImageToImageFilterVICF2VIF2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkImageToImageFilterVICF2VIF2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkImageToImageFilterVICF2VIF2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkImageToImageFilterVICF2VIF2.SetInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.GetInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.PushBackInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PushBackInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.PopBackInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PopBackInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.PushFrontInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PushFrontInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.PopFrontInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_PopFrontInput, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.SetCoordinateTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetCoordinateTolerance, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.GetCoordinateTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetCoordinateTolerance, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.SetDirectionTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_SetDirectionTolerance, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2.GetDirectionTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_GetDirectionTolerance, None, itkImageToImageFilterVICF2VIF2)
itkImageToImageFilterVICF2VIF2_swigregister = _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_swigregister
itkImageToImageFilterVICF2VIF2_swigregister(itkImageToImageFilterVICF2VIF2)

def itkImageToImageFilterVICF2VIF2_cast(obj: 'itkLightObject') -> "itkImageToImageFilterVICF2VIF2 *":
    """itkImageToImageFilterVICF2VIF2_cast(itkLightObject obj) -> itkImageToImageFilterVICF2VIF2"""
    return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF2VIF2_cast(obj)

class itkImageToImageFilterVICF3VIF3(itkImageSourcePython.itkImageSourceVIF3):
    """Proxy of C++ itkImageToImageFilterVICF3VIF3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def SetInput(self, *args) -> "void":
        """
        SetInput(itkImageToImageFilterVICF3VIF3 self, itkVectorImageCF3 image)
        SetInput(itkImageToImageFilterVICF3VIF3 self, unsigned int arg0, itkVectorImageCF3 image)
        """
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetInput(self, *args)


    def GetInput(self, *args) -> "itkVectorImageCF3 const *":
        """
        GetInput(itkImageToImageFilterVICF3VIF3 self) -> itkVectorImageCF3
        GetInput(itkImageToImageFilterVICF3VIF3 self, unsigned int idx) -> itkVectorImageCF3
        """
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetInput(self, *args)


    def PushBackInput(self, image: 'itkVectorImageCF3') -> "void":
        """PushBackInput(itkImageToImageFilterVICF3VIF3 self, itkVectorImageCF3 image)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PushBackInput(self, image)


    def PopBackInput(self) -> "void":
        """PopBackInput(itkImageToImageFilterVICF3VIF3 self)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PopBackInput(self)


    def PushFrontInput(self, image: 'itkVectorImageCF3') -> "void":
        """PushFrontInput(itkImageToImageFilterVICF3VIF3 self, itkVectorImageCF3 image)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PushFrontInput(self, image)


    def PopFrontInput(self) -> "void":
        """PopFrontInput(itkImageToImageFilterVICF3VIF3 self)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PopFrontInput(self)


    def SetCoordinateTolerance(self, _arg: 'double const') -> "void":
        """SetCoordinateTolerance(itkImageToImageFilterVICF3VIF3 self, double const _arg)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetCoordinateTolerance(self, _arg)


    def GetCoordinateTolerance(self) -> "double":
        """GetCoordinateTolerance(itkImageToImageFilterVICF3VIF3 self) -> double"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetCoordinateTolerance(self)


    def SetDirectionTolerance(self, _arg: 'double const') -> "void":
        """SetDirectionTolerance(itkImageToImageFilterVICF3VIF3 self, double const _arg)"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetDirectionTolerance(self, _arg)


    def GetDirectionTolerance(self) -> "double":
        """GetDirectionTolerance(itkImageToImageFilterVICF3VIF3 self) -> double"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetDirectionTolerance(self)

    __swig_destroy__ = _itkVectorInverseFFTImageFilterPython.delete_itkImageToImageFilterVICF3VIF3

    def cast(obj: 'itkLightObject') -> "itkImageToImageFilterVICF3VIF3 *":
        """cast(itkLightObject obj) -> itkImageToImageFilterVICF3VIF3"""
        return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkImageToImageFilterVICF3VIF3

        Create a new object of the class itkImageToImageFilterVICF3VIF3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkImageToImageFilterVICF3VIF3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkImageToImageFilterVICF3VIF3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkImageToImageFilterVICF3VIF3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkImageToImageFilterVICF3VIF3.SetInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.GetInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.PushBackInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PushBackInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.PopBackInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PopBackInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.PushFrontInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PushFrontInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.PopFrontInput = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_PopFrontInput, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.SetCoordinateTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetCoordinateTolerance, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.GetCoordinateTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetCoordinateTolerance, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.SetDirectionTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_SetDirectionTolerance, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3.GetDirectionTolerance = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_GetDirectionTolerance, None, itkImageToImageFilterVICF3VIF3)
itkImageToImageFilterVICF3VIF3_swigregister = _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_swigregister
itkImageToImageFilterVICF3VIF3_swigregister(itkImageToImageFilterVICF3VIF3)

def itkImageToImageFilterVICF3VIF3_cast(obj: 'itkLightObject') -> "itkImageToImageFilterVICF3VIF3 *":
    """itkImageToImageFilterVICF3VIF3_cast(itkLightObject obj) -> itkImageToImageFilterVICF3VIF3"""
    return _itkVectorInverseFFTImageFilterPython.itkImageToImageFilterVICF3VIF3_cast(obj)

class itkVectorInverseFFTImageFilterVICF2VIF2(itkImageToImageFilterVICF2VIF2):
    """Proxy of C++ itkVectorInverseFFTImageFilterVICF2VIF2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkVectorInverseFFTImageFilterVICF2VIF2_Pointer":
        """__New_orig__() -> itkVectorInverseFFTImageFilterVICF2VIF2_Pointer"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkVectorInverseFFTImageFilterVICF2VIF2_Pointer":
        """Clone(itkVectorInverseFFTImageFilterVICF2VIF2 self) -> itkVectorInverseFFTImageFilterVICF2VIF2_Pointer"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2_Clone(self)

    __swig_destroy__ = _itkVectorInverseFFTImageFilterPython.delete_itkVectorInverseFFTImageFilterVICF2VIF2

    def cast(obj: 'itkLightObject') -> "itkVectorInverseFFTImageFilterVICF2VIF2 *":
        """cast(itkLightObject obj) -> itkVectorInverseFFTImageFilterVICF2VIF2"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkVectorInverseFFTImageFilterVICF2VIF2

        Create a new object of the class itkVectorInverseFFTImageFilterVICF2VIF2 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkVectorInverseFFTImageFilterVICF2VIF2.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkVectorInverseFFTImageFilterVICF2VIF2.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkVectorInverseFFTImageFilterVICF2VIF2.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkVectorInverseFFTImageFilterVICF2VIF2.Clone = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2_Clone, None, itkVectorInverseFFTImageFilterVICF2VIF2)
itkVectorInverseFFTImageFilterVICF2VIF2_swigregister = _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2_swigregister
itkVectorInverseFFTImageFilterVICF2VIF2_swigregister(itkVectorInverseFFTImageFilterVICF2VIF2)

def itkVectorInverseFFTImageFilterVICF2VIF2___New_orig__() -> "itkVectorInverseFFTImageFilterVICF2VIF2_Pointer":
    """itkVectorInverseFFTImageFilterVICF2VIF2___New_orig__() -> itkVectorInverseFFTImageFilterVICF2VIF2_Pointer"""
    return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2___New_orig__()

def itkVectorInverseFFTImageFilterVICF2VIF2_cast(obj: 'itkLightObject') -> "itkVectorInverseFFTImageFilterVICF2VIF2 *":
    """itkVectorInverseFFTImageFilterVICF2VIF2_cast(itkLightObject obj) -> itkVectorInverseFFTImageFilterVICF2VIF2"""
    return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF2VIF2_cast(obj)

class itkVectorInverseFFTImageFilterVICF3VIF3(itkImageToImageFilterVICF3VIF3):
    """Proxy of C++ itkVectorInverseFFTImageFilterVICF3VIF3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')

    def __init__(self, *args, **kwargs):
        raise AttributeError("No constructor defined")
    __repr__ = _swig_repr

    def __New_orig__() -> "itkVectorInverseFFTImageFilterVICF3VIF3_Pointer":
        """__New_orig__() -> itkVectorInverseFFTImageFilterVICF3VIF3_Pointer"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3___New_orig__()

    __New_orig__ = staticmethod(__New_orig__)

    def Clone(self) -> "itkVectorInverseFFTImageFilterVICF3VIF3_Pointer":
        """Clone(itkVectorInverseFFTImageFilterVICF3VIF3 self) -> itkVectorInverseFFTImageFilterVICF3VIF3_Pointer"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3_Clone(self)

    __swig_destroy__ = _itkVectorInverseFFTImageFilterPython.delete_itkVectorInverseFFTImageFilterVICF3VIF3

    def cast(obj: 'itkLightObject') -> "itkVectorInverseFFTImageFilterVICF3VIF3 *":
        """cast(itkLightObject obj) -> itkVectorInverseFFTImageFilterVICF3VIF3"""
        return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3_cast(obj)

    cast = staticmethod(cast)

    def New(*args, **kargs):
        """New() -> itkVectorInverseFFTImageFilterVICF3VIF3

        Create a new object of the class itkVectorInverseFFTImageFilterVICF3VIF3 and set the input and the parameters if some
        named or non-named arguments are passed to that method.

        New() tries to assign all the non named parameters to the input of the new objects - the
        first non named parameter in the first input, etc.

        The named parameters are used by calling the method with the same name prefixed by 'Set'.

        Ex:

          itkVectorInverseFFTImageFilterVICF3VIF3.New( reader, Threshold=10 )

        is (most of the time) equivalent to:

          obj = itkVectorInverseFFTImageFilterVICF3VIF3.New()
          obj.SetInput( 0, reader.GetOutput() )
          obj.SetThreshold( 10 )
        """
        obj = itkVectorInverseFFTImageFilterVICF3VIF3.__New_orig__()
        import itkTemplate
        itkTemplate.New(obj, *args, **kargs)
        return obj
    New = staticmethod(New)

itkVectorInverseFFTImageFilterVICF3VIF3.Clone = new_instancemethod(_itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3_Clone, None, itkVectorInverseFFTImageFilterVICF3VIF3)
itkVectorInverseFFTImageFilterVICF3VIF3_swigregister = _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3_swigregister
itkVectorInverseFFTImageFilterVICF3VIF3_swigregister(itkVectorInverseFFTImageFilterVICF3VIF3)

def itkVectorInverseFFTImageFilterVICF3VIF3___New_orig__() -> "itkVectorInverseFFTImageFilterVICF3VIF3_Pointer":
    """itkVectorInverseFFTImageFilterVICF3VIF3___New_orig__() -> itkVectorInverseFFTImageFilterVICF3VIF3_Pointer"""
    return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3___New_orig__()

def itkVectorInverseFFTImageFilterVICF3VIF3_cast(obj: 'itkLightObject') -> "itkVectorInverseFFTImageFilterVICF3VIF3 *":
    """itkVectorInverseFFTImageFilterVICF3VIF3_cast(itkLightObject obj) -> itkVectorInverseFFTImageFilterVICF3VIF3"""
    return _itkVectorInverseFFTImageFilterPython.itkVectorInverseFFTImageFilterVICF3VIF3_cast(obj)


def image_to_image_filter(*args, **kwargs):
    """Procedural interface for ImageToImageFilter"""
    import itk
    return itk.ImageToImageFilter.__call__(*args, **kwargs)
def vector_inverse_fft_image_filter(*args, **kwargs):
    """Procedural interface for VectorInverseFFTImageFilter"""
    import itk
    return itk.VectorInverseFFTImageFilter.__call__(*args, **kwargs)



