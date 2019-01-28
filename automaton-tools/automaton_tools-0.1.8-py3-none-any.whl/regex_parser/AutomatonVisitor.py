from automaton_tools.regex_parser.grammar.RegexVisitor import *
from automaton_tools.regex_parser.Components import *
from automaton_tools.regex_parser.Automaton import AutomatonBuild
from automaton_tools.regex_parser.grammar.RegexParser import RegexParser

class AutomatonVisotor(RegexVisitor):

    def visitManyDigits(self, ctx: RegexParser.ManyDigitsContext):
        t = ctx.getText()
        num = int(t)
        return num

    def visitBasic(self, ctx: RegexParser.BasicContext):
        return self.visit( ctx.elementary() )

    def visitRoot(self, ctx: RegexParser.RootContext):
        return self.visit(ctx.re())

    def visitCharRule(self, ctx: RegexParser.CharRuleContext):
        c = self.visit(ctx.char())
        assert isinstance(c,CharSet)
        return AutomatonBuild.charset(c)

    def visitOrRule(self, ctx: RegexParser.OrRuleContext):
        a = self.visit(ctx.re(0))
        b = self.visit(ctx.re(1))
        return AutomatonBuild.orRule( a,b )

    def visitClosure(self, ctx: RegexParser.ClosureContext):
        t = self.visit(ctx.elementary())
        if ctx.op.text == "*":
            return AutomatonBuild.star(t)
        if ctx.op.text == "+":
            return AutomatonBuild.plus(t)

    def visitConcatenate(self, ctx: RegexParser.ConcatenateContext):
        a = self.visit(ctx.re(0))
        b = self.visit(ctx.re(1))
        assert type(a) == AutomatonBuild,"concat has to be basic component, but it is %s " % (type(a))
        return a.concat(b)

    def visitRepeatMin(self, ctx: RegexParser.RepeatMinContext):
        subre = self.visit(ctx.re())
        num = self.visit(ctx.digits())
        # create num subres the last one repeat itself
        import copy
        arrs = [ copy.deepcopy(subre) for _ in range(num) ] # deep copy necessary!
        t = arrs[0]
        arrs[-1] = AutomatonBuild.plus(arrs[-1])
        for i in range(len(arrs) - 1):
            t2 = arrs[i + 1]
            t = t.concat(t2)
        return t

    def visitOption(self, ctx: RegexParser.OptionContext):
        return AutomatonBuild.optional(self.visit(ctx.re()))

    def visitRepeatMinMax(self, ctx: RegexParser.RepeatMinMaxContext):
        subre = self.visit(ctx.re())
        num1 = self.visit(ctx.digits(0))
        num2 = self.visit(ctx.digits(1))
        # create num subres the last one repeat itself
        import copy
        arrs = [copy.deepcopy(subre) for _ in range(num1) ] # deep copy necessary! because of unique state

        mint = arrs[0]
        for i in range(len(arrs) - 1):
            t2 = arrs[i + 1]
            mint = mint.concat(t2)

        arrs2 = [copy.deepcopy(subre) for _ in range(num2 - num1)]
        starts_2 = [ i.start for i in arrs2]
        end2 = arrs2[-1].end
        maxt = arrs2[0]
        for i in range(len(arrs2) - 1):
            t2 = arrs2[i + 1]
            maxt = maxt.concat(t2)

        #last state of mint connect to all start in t2 and the last of t2
        end1 = mint.end
        edges = [ (end1,i,Edge_Epsilon) for i in starts_2 ]
        edges += [ (end1,end2,Edge_Epsilon) ]
        result = mint.concat(maxt)
        result.transition |= set(edges)
        return result

    def visitParenthesis(self, ctx: RegexParser.ParenthesisContext):
        return self.visit(ctx.re())

    def visitAny(self, ctx: RegexParser.AnyContext):
        return AutomatonBuild.charset( Char_ANY )

    def visitEos(self, ctx: RegexParser.EosContext):
        return AutomatonBuild.charset(Char_EOS)

    def visitStart(self, ctx: RegexParser.StartContext):
        return AutomatonBuild.charset(Char_START)

    def visitRange(self, ctx: RegexParser.RangeContext):
        return self.visit(ctx.range_expr())

    def visitNegativeSet(self, ctx: RegexParser.NegativeSetContext):
        charset = self.visit(ctx.range_item())
        charset.exclude = True
        return AutomatonBuild.charset(charset)

    def visitPositiveSet(self, ctx: RegexParser.PositiveSetContext):
        charset = self.visit(ctx.range_item())
        return AutomatonBuild.charset(charset)

    def visitSingleChar(self, ctx: RegexParser.SingleCharContext):
        single = self.visit(ctx.char())
        return CharRange({single.char})

    def visitConcatRangeItem(self, ctx: RegexParser.ConcatRangeItemContext):
        a = self.visit(ctx.range_item(0))
        b = self.visit(ctx.range_item(1))
        return CharRange(a.charset.union(b.charset))

    def visitCharRange(self, ctx: RegexParser.CharRangeContext):
        _from = self.visit(ctx.char(0))
        _to = self.visit(ctx.char(1))
        assert type(_from) is CharSet, "char range has to be a single character"
        assert type(_to) is CharSet, "char range has to be a single character"
        s = { chr(i) for i in range( ord(_from.char),ord(_to.char) + 1 ) }
        return CharRange(s)

    def visitCharacter(self, ctx: RegexParser.CharacterContext):
        ch = CharSet(ctx.getText())
        return ch

    def visitEscaped(self, ctx: RegexParser.EscapedContext):
        ch = ctx.getText()[-1]
        if ch == 'w':
            return Char_WORD
        if ch == 's':
            return Char_SPACE
        if ch == 'd':
            return Char_DIGIT
        #special chars
        if ch == 'n':
            return CharSet('\n')
        if ch == 't':
            return CharSet('\t')
        # for the rest, return the char itself
        return CharSet(ch)

