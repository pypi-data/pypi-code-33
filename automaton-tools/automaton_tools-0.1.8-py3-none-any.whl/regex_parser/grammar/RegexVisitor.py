# Generated from C:/Users/xiaochent/Downloads/automaton_tools-master/automaton_tools/regex_parser/grammar\Regex.g4 by ANTLR 4.7
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .RegexParser import RegexParser
else:
    from RegexParser import RegexParser

# This class defines a complete generic visitor for a parse tree produced by RegexParser.

class RegexVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RegexParser#root.
    def visitRoot(self, ctx:RegexParser.RootContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Basic.
    def visitBasic(self, ctx:RegexParser.BasicContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#OrRule.
    def visitOrRule(self, ctx:RegexParser.OrRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Closure.
    def visitClosure(self, ctx:RegexParser.ClosureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Concatenate.
    def visitConcatenate(self, ctx:RegexParser.ConcatenateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#RepeatMin.
    def visitRepeatMin(self, ctx:RegexParser.RepeatMinContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#RepeatMinMax.
    def visitRepeatMinMax(self, ctx:RegexParser.RepeatMinMaxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Option.
    def visitOption(self, ctx:RegexParser.OptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Parenthesis.
    def visitParenthesis(self, ctx:RegexParser.ParenthesisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Any.
    def visitAny(self, ctx:RegexParser.AnyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Eos.
    def visitEos(self, ctx:RegexParser.EosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Start.
    def visitStart(self, ctx:RegexParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#CharRule.
    def visitCharRule(self, ctx:RegexParser.CharRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Range.
    def visitRange(self, ctx:RegexParser.RangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#NegativeSet.
    def visitNegativeSet(self, ctx:RegexParser.NegativeSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#PositiveSet.
    def visitPositiveSet(self, ctx:RegexParser.PositiveSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#SingleChar.
    def visitSingleChar(self, ctx:RegexParser.SingleCharContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#ConcatRangeItem.
    def visitConcatRangeItem(self, ctx:RegexParser.ConcatRangeItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#CharRange.
    def visitCharRange(self, ctx:RegexParser.CharRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#ManyDigits.
    def visitManyDigits(self, ctx:RegexParser.ManyDigitsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Escaped.
    def visitEscaped(self, ctx:RegexParser.EscapedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#Character.
    def visitCharacter(self, ctx:RegexParser.CharacterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RegexParser#anyChar.
    def visitAnyChar(self, ctx:RegexParser.AnyCharContext):
        return self.visitChildren(ctx)



del RegexParser