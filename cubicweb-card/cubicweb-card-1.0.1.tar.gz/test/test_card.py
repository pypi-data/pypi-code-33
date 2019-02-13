"""template automatic tests"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC

class AutomaticWebTest(CubicWebTC):

    def to_test_etypes(self):
        return set(('Card',))


class CardTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.card = cnx.create_entity('Card', title=u'sample card', synopsis=u'this is a sample card').eid
            cnx.commit()

    def test_views(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.card)
            self.vreg['views'].select_or_none('inlined', fobj._cw, rset=fobj.cw_rset)

if __name__ == '__main__':
    unittest_main()
