# Generated from ./aslutils/ASL.g4 by ANTLR 4.5.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ASLParser import ASLParser
else:
    from ASLParser import ASLParser

# This class defines a complete generic visitor for a parse tree produced by ASLParser.

class ASLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ASLParser#start.
    def visitStart(self, ctx:ASLParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#statement.
    def visitStatement(self, ctx:ASLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#simpleStatement.
    def visitSimpleStatement(self, ctx:ASLParser.SimpleStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#block.
    def visitBlock(self, ctx:ASLParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#expression.
    def visitExpression(self, ctx:ASLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#assignableExpr.
    def visitAssignableExpr(self, ctx:ASLParser.AssignableExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#literal.
    def visitLiteral(self, ctx:ASLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ASLParser#typeName.
    def visitTypeName(self, ctx:ASLParser.TypeNameContext):
        return self.visitChildren(ctx)



del ASLParser