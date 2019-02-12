from .Tokens import Token
from typing import List

__all__ = [
    "ExprVisitor",
    "Expr",
    "Assign",
    "Binary",
    "Call",
    "Grouping",
    "Literal",
    "Logical",
    "Unary",
    "Variable",
]

class ExprVisitor:
    def visitAssignExpr(self, expr: "Assign"): raise NotImplementedError

    def visitBinaryExpr(self, expr: "Binary"): raise NotImplementedError

    def visitCallExpr(self, expr: "Call"): raise NotImplementedError

    def visitGroupingExpr(self, expr: "Grouping"): raise NotImplementedError

    def visitLiteralExpr(self, expr: "Literal"): raise NotImplementedError

    def visitLogicalExpr(self, expr: "Logical"): raise NotImplementedError

    def visitUnaryExpr(self, expr: "Unary"): raise NotImplementedError

    def visitVariableExpr(self, expr: "Variable"): raise NotImplementedError


class Expr:
    def accept(self, visitor: ExprVisitor): raise NotImplementedError



class Assign(Expr):

    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitAssignExpr(self)


class Binary(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visitBinaryExpr(self)


class Call(Expr):

    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: ExprVisitor):
        return visitor.visitCallExpr(self)


class Grouping(Expr):

    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: ExprVisitor):
        return visitor.visitGroupingExpr(self)


class Literal(Expr):

    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLiteralExpr(self)


class Logical(Expr):

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visitLogicalExpr(self)


class Unary(Expr):

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: ExprVisitor):
        return visitor.visitUnaryExpr(self)


class Variable(Expr):

    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: ExprVisitor):
        return visitor.visitVariableExpr(self)


    