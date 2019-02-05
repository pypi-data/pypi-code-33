depends = ('ITKPyBase', 'ITKImageSources', 'ITKImageIntensity', 'ITKImageFilterBase', 'ITKDistanceMap', 'ITKCommon', 'BinaryThinning3D', )
templates = (
  ('MedialThicknessImageFilter3D', 'itk::MedialThicknessImageFilter3D', 'itkMedialThicknessImageFilter3DISS3IF3', True, 'itk::Image< signed short,3 >, itk::Image< float,3 >'),
  ('MedialThicknessImageFilter3D', 'itk::MedialThicknessImageFilter3D', 'itkMedialThicknessImageFilter3DIUC3IF3', True, 'itk::Image< unsigned char,3 >, itk::Image< float,3 >'),
  ('MedialThicknessImageFilter3D', 'itk::MedialThicknessImageFilter3D', 'itkMedialThicknessImageFilter3DIUS3IF3', True, 'itk::Image< unsigned short,3 >, itk::Image< float,3 >'),
  ('MedialThicknessImageFilter3D', 'itk::MedialThicknessImageFilter3D', 'itkMedialThicknessImageFilter3DIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
)
snake_case_functions = ('medial_thickness_image_filter3_d', )
