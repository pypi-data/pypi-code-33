from sqlalchemy.testing import fixtures, config, eq_
from sqlalchemy import Column, INTEGER, JSON, Table, MetaData
from sqlalchemy.schema import Table as schematable

class TableCommentTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        cls.engine = metadata.bind
        Table("json_table", metadata,
              Column('id', INTEGER, primary_key=True),
              comment="test_comment"
              )


    def _assert_result(self, select, result):
        eq_(
            config.db.execute(select).fetchall(),
            result
        )

    def test_simple_comment(self):
        metadata = MetaData(bind=self.engine)
        t = schematable("json_table", metadata, autoload=True)
        eq_(t.comment, "test_comment")