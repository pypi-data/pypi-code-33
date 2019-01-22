# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (3, 0, 0):
    new_instancemethod = lambda func, inst, cls: _itkRieszRotationMatrixPython.SWIG_PyInstanceMethod_New(func)
else:
    from new import instancemethod as new_instancemethod
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_itkRieszRotationMatrixPython', [dirname(__file__)])
        except ImportError:
            import _itkRieszRotationMatrixPython
            return _itkRieszRotationMatrixPython
        if fp is not None:
            try:
                _mod = imp.load_module('_itkRieszRotationMatrixPython', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _itkRieszRotationMatrixPython = swig_import_helper()
    del swig_import_helper
else:
    import _itkRieszRotationMatrixPython
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


import itkVariableSizeMatrixPython
import itkArrayPython
import vnl_vectorPython
import stdcomplexPython
import pyBasePython
import vnl_matrixPython
import itkMatrixPython
import vnl_matrix_fixedPython
import itkVectorPython
import vnl_vector_refPython
import itkFixedArrayPython
import itkPointPython
import itkCovariantVectorPython
class itkRieszRotationMatrixD2(itkVariableSizeMatrixPython.itkVariableSizeMatrixD):
    """Proxy of C++ itkRieszRotationMatrixD2 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def ComputeSteerableMatrix(self) -> "vnl_matrixD const &":
        """ComputeSteerableMatrix(itkRieszRotationMatrixD2 self) -> vnl_matrixD"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_ComputeSteerableMatrix(self)


    def GenerateIndicesMatrix(self) -> "std::vector< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > >,std::allocator< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > > > >":
        """GenerateIndicesMatrix(itkRieszRotationMatrixD2 self) -> std::vector< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > >,std::allocator< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > > > >"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GenerateIndicesMatrix(self)


    def __init__(self, *args):
        """
        __init__(itkRieszRotationMatrixD2 self) -> itkRieszRotationMatrixD2
        __init__(itkRieszRotationMatrixD2 self, itkRieszRotationMatrixD2 matrix) -> itkRieszRotationMatrixD2
        __init__(itkRieszRotationMatrixD2 self, itkMatrixD22 spatialRotationMatrix, unsigned int const & order) -> itkRieszRotationMatrixD2
        """
        _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_swiginit(self, _itkRieszRotationMatrixPython.new_itkRieszRotationMatrixD2(*args))

    def GetOrder(self) -> "unsigned int const &":
        """GetOrder(itkRieszRotationMatrixD2 self) -> unsigned int const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetOrder(self)


    def SetOrder(self, order: 'unsigned int const &') -> "void":
        """SetOrder(itkRieszRotationMatrixD2 self, unsigned int const & order)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetOrder(self, order)


    def GetComponents(self) -> "unsigned int const &":
        """GetComponents(itkRieszRotationMatrixD2 self) -> unsigned int const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetComponents(self)


    def GetSpatialRotationMatrix(self) -> "itkMatrixD22 const &":
        """GetSpatialRotationMatrix(itkRieszRotationMatrixD2 self) -> itkMatrixD22"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetSpatialRotationMatrix(self)


    def SetSpatialRotationMatrix(self, spatialRotationMatrix: 'itkMatrixD22') -> "void":
        """SetSpatialRotationMatrix(itkRieszRotationMatrixD2 self, itkMatrixD22 spatialRotationMatrix)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetSpatialRotationMatrix(self, spatialRotationMatrix)


    def GetMaxAbsoluteDifferenceCloseToZero(self) -> "double const &":
        """GetMaxAbsoluteDifferenceCloseToZero(itkRieszRotationMatrixD2 self) -> double const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetMaxAbsoluteDifferenceCloseToZero(self)


    def SetMaxAbsoluteDifferenceCloseToZero(self, maxAbsoluteDifference: 'double const &') -> "void":
        """SetMaxAbsoluteDifferenceCloseToZero(itkRieszRotationMatrixD2 self, double const & maxAbsoluteDifference)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetMaxAbsoluteDifferenceCloseToZero(self, maxAbsoluteDifference)


    def GetDebug(self) -> "bool const &":
        """GetDebug(itkRieszRotationMatrixD2 self) -> bool const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetDebug(self)


    def SetDebug(self, boolean: 'bool const &') -> "void":
        """SetDebug(itkRieszRotationMatrixD2 self, bool const & boolean)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebug(self, boolean)


    def SetDebugOn(self) -> "void":
        """SetDebugOn(itkRieszRotationMatrixD2 self)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebugOn(self)


    def SetDebugOff(self) -> "void":
        """SetDebugOff(itkRieszRotationMatrixD2 self)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebugOff(self)

    __swig_destroy__ = _itkRieszRotationMatrixPython.delete_itkRieszRotationMatrixD2
itkRieszRotationMatrixD2.ComputeSteerableMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_ComputeSteerableMatrix, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GenerateIndicesMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GenerateIndicesMatrix, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GetOrder = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetOrder, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetOrder = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetOrder, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GetComponents = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetComponents, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GetSpatialRotationMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetSpatialRotationMatrix, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetSpatialRotationMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetSpatialRotationMatrix, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GetMaxAbsoluteDifferenceCloseToZero = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetMaxAbsoluteDifferenceCloseToZero, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetMaxAbsoluteDifferenceCloseToZero = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetMaxAbsoluteDifferenceCloseToZero, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.GetDebug = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_GetDebug, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetDebug = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebug, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetDebugOn = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebugOn, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2.SetDebugOff = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_SetDebugOff, None, itkRieszRotationMatrixD2)
itkRieszRotationMatrixD2_swigregister = _itkRieszRotationMatrixPython.itkRieszRotationMatrixD2_swigregister
itkRieszRotationMatrixD2_swigregister(itkRieszRotationMatrixD2)

class itkRieszRotationMatrixD3(itkVariableSizeMatrixPython.itkVariableSizeMatrixD):
    """Proxy of C++ itkRieszRotationMatrixD3 class."""

    thisown = _swig_property(lambda x: x.this.own(), lambda x, v: x.this.own(v), doc='The membership flag')
    __repr__ = _swig_repr

    def ComputeSteerableMatrix(self) -> "vnl_matrixD const &":
        """ComputeSteerableMatrix(itkRieszRotationMatrixD3 self) -> vnl_matrixD"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_ComputeSteerableMatrix(self)


    def GenerateIndicesMatrix(self) -> "std::vector< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > >,std::allocator< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > > > >":
        """GenerateIndicesMatrix(itkRieszRotationMatrixD3 self) -> std::vector< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > >,std::allocator< std::vector< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > >,std::allocator< std::vector< std::vector< unsigned int,std::allocator< unsigned int > >,std::allocator< std::vector< unsigned int,std::allocator< unsigned int > > > > > > > >"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GenerateIndicesMatrix(self)


    def __init__(self, *args):
        """
        __init__(itkRieszRotationMatrixD3 self) -> itkRieszRotationMatrixD3
        __init__(itkRieszRotationMatrixD3 self, itkRieszRotationMatrixD3 matrix) -> itkRieszRotationMatrixD3
        __init__(itkRieszRotationMatrixD3 self, itkMatrixD33 spatialRotationMatrix, unsigned int const & order) -> itkRieszRotationMatrixD3
        """
        _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_swiginit(self, _itkRieszRotationMatrixPython.new_itkRieszRotationMatrixD3(*args))

    def GetOrder(self) -> "unsigned int const &":
        """GetOrder(itkRieszRotationMatrixD3 self) -> unsigned int const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetOrder(self)


    def SetOrder(self, order: 'unsigned int const &') -> "void":
        """SetOrder(itkRieszRotationMatrixD3 self, unsigned int const & order)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetOrder(self, order)


    def GetComponents(self) -> "unsigned int const &":
        """GetComponents(itkRieszRotationMatrixD3 self) -> unsigned int const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetComponents(self)


    def GetSpatialRotationMatrix(self) -> "itkMatrixD33 const &":
        """GetSpatialRotationMatrix(itkRieszRotationMatrixD3 self) -> itkMatrixD33"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetSpatialRotationMatrix(self)


    def SetSpatialRotationMatrix(self, spatialRotationMatrix: 'itkMatrixD33') -> "void":
        """SetSpatialRotationMatrix(itkRieszRotationMatrixD3 self, itkMatrixD33 spatialRotationMatrix)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetSpatialRotationMatrix(self, spatialRotationMatrix)


    def GetMaxAbsoluteDifferenceCloseToZero(self) -> "double const &":
        """GetMaxAbsoluteDifferenceCloseToZero(itkRieszRotationMatrixD3 self) -> double const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetMaxAbsoluteDifferenceCloseToZero(self)


    def SetMaxAbsoluteDifferenceCloseToZero(self, maxAbsoluteDifference: 'double const &') -> "void":
        """SetMaxAbsoluteDifferenceCloseToZero(itkRieszRotationMatrixD3 self, double const & maxAbsoluteDifference)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetMaxAbsoluteDifferenceCloseToZero(self, maxAbsoluteDifference)


    def GetDebug(self) -> "bool const &":
        """GetDebug(itkRieszRotationMatrixD3 self) -> bool const &"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetDebug(self)


    def SetDebug(self, boolean: 'bool const &') -> "void":
        """SetDebug(itkRieszRotationMatrixD3 self, bool const & boolean)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebug(self, boolean)


    def SetDebugOn(self) -> "void":
        """SetDebugOn(itkRieszRotationMatrixD3 self)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebugOn(self)


    def SetDebugOff(self) -> "void":
        """SetDebugOff(itkRieszRotationMatrixD3 self)"""
        return _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebugOff(self)

    __swig_destroy__ = _itkRieszRotationMatrixPython.delete_itkRieszRotationMatrixD3
itkRieszRotationMatrixD3.ComputeSteerableMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_ComputeSteerableMatrix, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GenerateIndicesMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GenerateIndicesMatrix, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GetOrder = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetOrder, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetOrder = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetOrder, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GetComponents = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetComponents, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GetSpatialRotationMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetSpatialRotationMatrix, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetSpatialRotationMatrix = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetSpatialRotationMatrix, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GetMaxAbsoluteDifferenceCloseToZero = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetMaxAbsoluteDifferenceCloseToZero, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetMaxAbsoluteDifferenceCloseToZero = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetMaxAbsoluteDifferenceCloseToZero, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.GetDebug = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_GetDebug, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetDebug = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebug, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetDebugOn = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebugOn, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3.SetDebugOff = new_instancemethod(_itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_SetDebugOff, None, itkRieszRotationMatrixD3)
itkRieszRotationMatrixD3_swigregister = _itkRieszRotationMatrixPython.itkRieszRotationMatrixD3_swigregister
itkRieszRotationMatrixD3_swigregister(itkRieszRotationMatrixD3)



