from typing import List

from .Tokens import TokenType, Token
from .Expr import *


class AstPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visitBinaryExpr(self, expr: Binary):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Grouping):
        return self.parenthesize("group", expr.expression)  # REVIEW: group 需要主动命名

    def visitLiteralExpr(self, expr: Literal):
        return str(expr.value)  # REVIEW: 之前误写成 self.parenthesize(str(expr.value)) Literal 是 terminal

    def visitUnaryExpr(self, expr: Unary):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs: Expr):
        return '( {} {} )'.format(name, ' '.join([expr.accept(self) for expr in exprs]))


def main():
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal(45.67)))

    print(AstPrinter().print(expression))


if __name__ == '__main__':
    main()
