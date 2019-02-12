from .Tokens import Token
from typing import List

__all__ = [
    "StmtVisitor",
    "Stmt",
    "Block",
    "If",
    "Function",
    "Expression",
    "Print",
    "Return",
    "Var",
    "While",
]

class StmtVisitor:
    def visitBlockStmt(self, stmt: "Block"): raise NotImplementedError

    def visitIfStmt(self, stmt: "If"): raise NotImplementedError

    def visitFunctionStmt(self, stmt: "Function"): raise NotImplementedError

    def visitExpressionStmt(self, stmt: "Expression"): raise NotImplementedError

    def visitPrintStmt(self, stmt: "Print"): raise NotImplementedError

    def visitReturnStmt(self, stmt: "Return"): raise NotImplementedError

    def visitVarStmt(self, stmt: "Var"): raise NotImplementedError

    def visitWhileStmt(self, stmt: "While"): raise NotImplementedError


class Stmt:
    def accept(self, visitor: StmtVisitor): raise NotImplementedError



class Block(Stmt):

    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visitBlockStmt(self)


class If(Stmt):

    def __init__(self, condition: 'Expr', thenBranch: Stmt, elseBranch: Stmt):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

    def accept(self, visitor: StmtVisitor):
        return visitor.visitIfStmt(self)


class Function(Stmt):

    def __init__(self, name: Token, parameters: List[Token], body: List[Stmt]):
        self.name = name
        self.parameters = parameters
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visitFunctionStmt(self)


class Expression(Stmt):

    def __init__(self, expression: 'Expr'):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visitExpressionStmt(self)


class Print(Stmt):

    def __init__(self, expression: 'Expr'):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visitPrintStmt(self)


class Return(Stmt):

    def __init__(self, keyword: Token, value: 'Expr'):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor):
        return visitor.visitReturnStmt(self)


class Var(Stmt):

    def __init__(self, name: Token, initializer: 'Expr'):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visitVarStmt(self)


class While(Stmt):

    def __init__(self, condition: 'Expr', body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visitWhileStmt(self)


    