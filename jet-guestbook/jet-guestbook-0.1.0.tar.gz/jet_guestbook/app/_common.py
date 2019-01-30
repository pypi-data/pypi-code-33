from marshmallow import Schema, fields


class _VisitPath(Schema):
    visit_id = fields.Integer()


class _VisitorPath(Schema):
    visitor_id = fields.Integer()


class _VisitPathFull(_VisitorPath, _VisitPath):
    pass
