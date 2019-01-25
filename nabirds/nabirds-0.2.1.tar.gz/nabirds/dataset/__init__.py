from .mixins.reading import AnnotationsReadMixin, ImageListReadingMixin
from .mixins.parts import PartMixin, RevealedPartMixin, CroppedPartMixin
from .mixins.features import PreExtractedFeaturesMixin

class Dataset(PartMixin, PreExtractedFeaturesMixin, AnnotationsReadMixin):

	def get_example(self, i):
		im_obj = super(Dataset, self).get_example(i)
		return im_obj.as_tuple()
