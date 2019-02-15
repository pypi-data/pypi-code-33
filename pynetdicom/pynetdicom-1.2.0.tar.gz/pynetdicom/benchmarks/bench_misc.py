"""Miscellaneous benchmarks for testing optmisations."""

from pydicom import Dataset
from pynetdicom.service_class import StorageServiceClass


class TimeCodeSnippets(object):
    """

    Conclusions
    -----------
    * time_get_attr is twice as fast as time_has_attr, but we're only talking
      about 66.2 vs 32.6 ms per 10k runs (if AffectedSOPClassUID) and
      85.9 vs 56.2 ms per 10k run (if RequestedSOPClassUID).
    * Caching the StorageService class instance is faster than creating a
      new instance every run (2.67 ms vs 0.29 ms per 10k runs), but the time
      it takes to init is tiny anyway.

    """
    def setup(self):
        """Setup the test"""
        self.ds = Dataset()
        #self.ds.AffectedSOPClassUID = '1.2.3.4.5.6.7.8.9.10'
        self.ds.RequestedSOPClassUID = '1.2.3.4.5.6.3.2'
        self.no_runs = 10000

    def time_has_attr(self):
        """Time testing the element then assigning."""
        for ii in range(self.no_runs):

            if getattr(self.ds, 'AffectedSOPClassUID', None) is not None:
                class_uid = self.ds.AffectedSOPClassUID
            elif getattr(self.ds, 'RequestedSOPClassUID', None) is not None:
                class_uid = self.ds.RequestedSOPClassUID
            else:
                continue

    def time_get_attr(self):
        """Time getting the element then testing"""
        for ii in range(self.no_runs):

            class_uid = getattr(self.ds, 'AffectedSOPClassUID', None)
            if not class_uid:
                class_uid = getattr(self.ds, 'RequestedSOPClassUID', None)
            if not class_uid:
                continue

    def time_cache_service_class(self):
        """Test caching the StorageServiceClass instance."""
        _cache = None
        _uid = None
        for ii in range(self.no_runs):
            if _uid == '1.2.3':
                pass
            else:
                service = StorageServiceClass(None)
                _cache = service
                _uid = '1.2.3'

    def time_nocache_service_class(self):
        """Test initiating a new instance of StorageServiceClass every run."""
        for ii in range(self.no_runs):
            service = StorageServiceClass(None)
