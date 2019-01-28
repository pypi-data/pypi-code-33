from automaton_tools.regex_parser.Components import *
from automaton_tools.regex_parser.Automaton import AutomatonBuild
from automaton_tools.regex_parser.grammar.RegexParser import RegexParser

from .AST import *
from .AutomatonVisitor import AutomatonVisotor

class ASTVisitor(AutomatonVisotor):

    def visitNegativeSet(self, ctx: RegexParser.NegativeSetContext):
        charset = self.visit(ctx.range_item())
        charset.exclude = True
        return CharsetAST(charset)

    def visitPositiveSet(self, ctx: RegexParser.PositiveSetContext):
        charset = self.visit(ctx.range_item())
        return CharsetAST(charset)

    def visitCharRule(self, ctx: RegexParser.CharRuleContext):
        c = self.visit(ctx.char())
        assert isinstance(c,CharSet)
        return CharsetAST(c)

    def visitOrRule(self, ctx: RegexParser.OrRuleContext):
        a = self.visit(ctx.re(0))
        b = self.visit(ctx.re(1))
        return OrAST(a,b)

    def visitClosure(self, ctx: RegexParser.ClosureContext):
        t = self.visit(ctx.elementary())
        if ctx.op.text == "*":
            return StarAST(t)
        if ctx.op.text == "+":
            return PlusAST(t)

    def visitConcatenate(self, ctx: RegexParser.ConcatenateContext):
        a = self.visit(ctx.re(0))
        b = self.visit(ctx.re(1))
        assert isinstance(a,AST), "concat has to be AST, but it is %s " % (type(a))
        return ConcatAST(a, b)

    def visitRepeatMin(self, ctx: RegexParser.RepeatMinContext):
        subre = self.visit(ctx.re())
        num = self.visit(ctx.digits())
        # create num subres the last one repeat itself
        return RepeatAST(subre,num,None)

    def visitOption(self, ctx: RegexParser.OptionContext):
        return OptionAST(ctx.re())

    def visitRepeatMinMax(self, ctx: RegexParser.RepeatMinMaxContext):
        subre = self.visit(ctx.re())
        num1 = self.visit(ctx.digits(0))
        num2 = self.visit(ctx.digits(1))
        return RepeatAST(subre,num1,num2)

    def visitAny(self, ctx: RegexParser.AnyContext):
        return CharsetAST( Char_ANY )

    def visitEos(self, ctx: RegexParser.EosContext):
        return CharsetAST(Char_EOS)

    def visitStart(self, ctx: RegexParser.StartContext):
        return CharsetAST(Char_START)

