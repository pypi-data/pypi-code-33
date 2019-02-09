from pyquilted.quilted.work import *


class WorkMapper:
    def __init__(self, work_odict):
        self.work = Work()
        self.odict = work_odict

    def deserialize(self):
        for key, val in self.odict.items():
            self._work_mapper(key, val)
        return self.work

    def _work_mapper(self, key, val):
        if key in 'other':
            slugs = Slugs(list(val))
            self.work.add_slugs(vars(slugs))
        else:
            job = self._create_job(key, val)
            self.work.add_job(job)

    def _create_job(self, key, data):
        self._add_company_to_data(key, data)
        job = Job(**data)
        return job

    def _add_company_to_data(self, company, data):
        data['company'] = company
