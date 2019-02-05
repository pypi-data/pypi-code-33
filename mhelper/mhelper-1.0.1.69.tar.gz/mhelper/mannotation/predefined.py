from mhelper.mannotation.classes import MAnnotation
from mhelper.mannotation.predefined_classes import FileNameAnnotation


isOptionList = MAnnotation( "isOptionList" )
isFilename = FileNameAnnotation( "isFilename", str )
isDirname = MAnnotation( "isDirname", str )
isOptional = MAnnotation( "isOptional" )
isUnion = MAnnotation( "isUnion" )
isReadonly = MAnnotation( "isReadonly" )
isPassword = MAnnotation( "isPassword", str )