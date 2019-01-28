# Generated from C:/Users/xiaochent/Downloads/automaton_tools-master/automaton_tools/regex_parser/grammar\Regex.g4 by ANTLR 4.7
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\26")
        buf.write("e\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3\3\5\3\33\n")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\3\3\3\3\7\3\61\n\3\f\3\16\3\64\13")
        buf.write("\3\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4?\n\4\3\5\3")
        buf.write("\5\3\5\3\5\3\5\3\5\3\5\3\5\5\5I\n\5\3\6\3\6\3\6\3\6\3")
        buf.write("\6\3\6\5\6Q\n\6\3\6\3\6\7\6U\n\6\f\6\16\6X\13\6\3\7\6")
        buf.write("\7[\n\7\r\7\16\7\\\3\b\3\b\5\ba\n\b\3\t\3\t\3\t\2\4\4")
        buf.write("\n\n\2\4\6\b\n\f\16\20\2\4\3\2\3\4\4\2\23\23\25\26\2l")
        buf.write("\2\22\3\2\2\2\4\32\3\2\2\2\6>\3\2\2\2\bH\3\2\2\2\nP\3")
        buf.write("\2\2\2\fZ\3\2\2\2\16`\3\2\2\2\20b\3\2\2\2\22\23\5\4\3")
        buf.write("\2\23\24\7\2\2\3\24\3\3\2\2\2\25\26\b\3\1\2\26\27\5\6")
        buf.write("\4\2\27\30\t\2\2\2\30\33\3\2\2\2\31\33\5\6\4\2\32\25\3")
        buf.write("\2\2\2\32\31\3\2\2\2\33\62\3\2\2\2\34\35\f\4\2\2\35\61")
        buf.write("\5\4\3\5\36\37\f\3\2\2\37 \7\t\2\2 \61\5\4\3\4!\"\f\b")
        buf.write("\2\2\"#\7\5\2\2#$\5\f\7\2$%\7\6\2\2%&\7\7\2\2&\61\3\2")
        buf.write("\2\2\'(\f\7\2\2()\7\5\2\2)*\5\f\7\2*+\7\6\2\2+,\5\f\7")
        buf.write("\2,-\7\7\2\2-\61\3\2\2\2./\f\5\2\2/\61\7\b\2\2\60\34\3")
        buf.write("\2\2\2\60\36\3\2\2\2\60!\3\2\2\2\60\'\3\2\2\2\60.\3\2")
        buf.write("\2\2\61\64\3\2\2\2\62\60\3\2\2\2\62\63\3\2\2\2\63\5\3")
        buf.write("\2\2\2\64\62\3\2\2\2\65\66\7\n\2\2\66\67\5\4\3\2\678\7")
        buf.write("\13\2\28?\3\2\2\29?\7\f\2\2:?\7\r\2\2;?\7\16\2\2<?\5\16")
        buf.write("\b\2=?\5\b\5\2>\65\3\2\2\2>9\3\2\2\2>:\3\2\2\2>;\3\2\2")
        buf.write("\2><\3\2\2\2>=\3\2\2\2?\7\3\2\2\2@A\7\17\2\2AB\5\n\6\2")
        buf.write("BC\7\20\2\2CI\3\2\2\2DE\7\21\2\2EF\5\n\6\2FG\7\20\2\2")
        buf.write("GI\3\2\2\2H@\3\2\2\2HD\3\2\2\2I\t\3\2\2\2JK\b\6\1\2KL")
        buf.write("\5\16\b\2LM\7\22\2\2MN\5\16\b\2NQ\3\2\2\2OQ\5\16\b\2P")
        buf.write("J\3\2\2\2PO\3\2\2\2QV\3\2\2\2RS\f\5\2\2SU\5\n\6\6TR\3")
        buf.write("\2\2\2UX\3\2\2\2VT\3\2\2\2VW\3\2\2\2W\13\3\2\2\2XV\3\2")
        buf.write("\2\2Y[\7\23\2\2ZY\3\2\2\2[\\\3\2\2\2\\Z\3\2\2\2\\]\3\2")
        buf.write("\2\2]\r\3\2\2\2^a\7\24\2\2_a\5\20\t\2`^\3\2\2\2`_\3\2")
        buf.write("\2\2a\17\3\2\2\2bc\t\3\2\2c\21\3\2\2\2\13\32\60\62>HP")
        buf.write("V\\`")
        return buf.getvalue()


class RegexParser ( Parser ):

    grammarFileName = "Regex.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'*'", "'+'", "'{'", "','", "'}'", "'?'", 
                     "'|'", "'('", "')'", "'.'", "'$'", "'^'", "'[^'", "']'", 
                     "'['", "'-'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "Digit", "EscapedChar", "Punctuation", 
                      "Letter" ]

    RULE_root = 0
    RULE_re = 1
    RULE_elementary = 2
    RULE_range_expr = 3
    RULE_range_item = 4
    RULE_digits = 5
    RULE_char = 6
    RULE_anyChar = 7

    ruleNames =  [ "root", "re", "elementary", "range_expr", "range_item", 
                   "digits", "char", "anyChar" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    Digit=17
    EscapedChar=18
    Punctuation=19
    Letter=20

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class RootContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def re(self):
            return self.getTypedRuleContext(RegexParser.ReContext,0)


        def EOF(self):
            return self.getToken(RegexParser.EOF, 0)

        def getRuleIndex(self):
            return RegexParser.RULE_root

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRoot" ):
                return visitor.visitRoot(self)
            else:
                return visitor.visitChildren(self)




    def root(self):

        localctx = RegexParser.RootContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_root)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.re(0)
            self.state = 17
            self.match(RegexParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ReContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_re

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class BasicContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def elementary(self):
            return self.getTypedRuleContext(RegexParser.ElementaryContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBasic" ):
                return visitor.visitBasic(self)
            else:
                return visitor.visitChildren(self)


    class OrRuleContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RegexParser.ReContext)
            else:
                return self.getTypedRuleContext(RegexParser.ReContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrRule" ):
                return visitor.visitOrRule(self)
            else:
                return visitor.visitChildren(self)


    class ClosureContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def elementary(self):
            return self.getTypedRuleContext(RegexParser.ElementaryContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitClosure" ):
                return visitor.visitClosure(self)
            else:
                return visitor.visitChildren(self)


    class ConcatenateContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RegexParser.ReContext)
            else:
                return self.getTypedRuleContext(RegexParser.ReContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConcatenate" ):
                return visitor.visitConcatenate(self)
            else:
                return visitor.visitChildren(self)


    class RepeatMinContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self):
            return self.getTypedRuleContext(RegexParser.ReContext,0)

        def digits(self):
            return self.getTypedRuleContext(RegexParser.DigitsContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRepeatMin" ):
                return visitor.visitRepeatMin(self)
            else:
                return visitor.visitChildren(self)


    class RepeatMinMaxContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self):
            return self.getTypedRuleContext(RegexParser.ReContext,0)

        def digits(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RegexParser.DigitsContext)
            else:
                return self.getTypedRuleContext(RegexParser.DigitsContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRepeatMinMax" ):
                return visitor.visitRepeatMinMax(self)
            else:
                return visitor.visitChildren(self)


    class OptionContext(ReContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ReContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self):
            return self.getTypedRuleContext(RegexParser.ReContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOption" ):
                return visitor.visitOption(self)
            else:
                return visitor.visitChildren(self)



    def re(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = RegexParser.ReContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_re, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                localctx = RegexParser.ClosureContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 20
                self.elementary()
                self.state = 21
                localctx.op = self._input.LT(1)
                _la = self._input.LA(1)
                if not(_la==RegexParser.T__0 or _la==RegexParser.T__1):
                    localctx.op = self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass

            elif la_ == 2:
                localctx = RegexParser.BasicContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 23
                self.elementary()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 48
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 46
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                    if la_ == 1:
                        localctx = RegexParser.ConcatenateContext(self, RegexParser.ReContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_re)
                        self.state = 26
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 27
                        self.re(3)
                        pass

                    elif la_ == 2:
                        localctx = RegexParser.OrRuleContext(self, RegexParser.ReContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_re)
                        self.state = 28
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 29
                        self.match(RegexParser.T__6)
                        self.state = 30
                        self.re(2)
                        pass

                    elif la_ == 3:
                        localctx = RegexParser.RepeatMinContext(self, RegexParser.ReContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_re)
                        self.state = 31
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 32
                        self.match(RegexParser.T__2)
                        self.state = 33
                        self.digits()
                        self.state = 34
                        self.match(RegexParser.T__3)
                        self.state = 35
                        self.match(RegexParser.T__4)
                        pass

                    elif la_ == 4:
                        localctx = RegexParser.RepeatMinMaxContext(self, RegexParser.ReContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_re)
                        self.state = 37
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 38
                        self.match(RegexParser.T__2)
                        self.state = 39
                        self.digits()
                        self.state = 40
                        self.match(RegexParser.T__3)
                        self.state = 41
                        self.digits()
                        self.state = 42
                        self.match(RegexParser.T__4)
                        pass

                    elif la_ == 5:
                        localctx = RegexParser.OptionContext(self, RegexParser.ReContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_re)
                        self.state = 44
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 45
                        self.match(RegexParser.T__5)
                        pass

             
                self.state = 50
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class ElementaryContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_elementary

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ParenthesisContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def re(self):
            return self.getTypedRuleContext(RegexParser.ReContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenthesis" ):
                return visitor.visitParenthesis(self)
            else:
                return visitor.visitChildren(self)


    class StartContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStart" ):
                return visitor.visitStart(self)
            else:
                return visitor.visitChildren(self)


    class EosContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEos" ):
                return visitor.visitEos(self)
            else:
                return visitor.visitChildren(self)


    class CharRuleContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def char(self):
            return self.getTypedRuleContext(RegexParser.CharContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCharRule" ):
                return visitor.visitCharRule(self)
            else:
                return visitor.visitChildren(self)


    class RangeContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def range_expr(self):
            return self.getTypedRuleContext(RegexParser.Range_exprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRange" ):
                return visitor.visitRange(self)
            else:
                return visitor.visitChildren(self)


    class AnyContext(ElementaryContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.ElementaryContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAny" ):
                return visitor.visitAny(self)
            else:
                return visitor.visitChildren(self)



    def elementary(self):

        localctx = RegexParser.ElementaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_elementary)
        try:
            self.state = 60
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [RegexParser.T__7]:
                localctx = RegexParser.ParenthesisContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 51
                self.match(RegexParser.T__7)
                self.state = 52
                self.re(0)
                self.state = 53
                self.match(RegexParser.T__8)
                pass
            elif token in [RegexParser.T__9]:
                localctx = RegexParser.AnyContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 55
                self.match(RegexParser.T__9)
                pass
            elif token in [RegexParser.T__10]:
                localctx = RegexParser.EosContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 56
                self.match(RegexParser.T__10)
                pass
            elif token in [RegexParser.T__11]:
                localctx = RegexParser.StartContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 57
                self.match(RegexParser.T__11)
                pass
            elif token in [RegexParser.Digit, RegexParser.EscapedChar, RegexParser.Punctuation, RegexParser.Letter]:
                localctx = RegexParser.CharRuleContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 58
                self.char()
                pass
            elif token in [RegexParser.T__12, RegexParser.T__14]:
                localctx = RegexParser.RangeContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 59
                self.range_expr()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Range_exprContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_range_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class NegativeSetContext(Range_exprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.Range_exprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def range_item(self):
            return self.getTypedRuleContext(RegexParser.Range_itemContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNegativeSet" ):
                return visitor.visitNegativeSet(self)
            else:
                return visitor.visitChildren(self)


    class PositiveSetContext(Range_exprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.Range_exprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def range_item(self):
            return self.getTypedRuleContext(RegexParser.Range_itemContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPositiveSet" ):
                return visitor.visitPositiveSet(self)
            else:
                return visitor.visitChildren(self)



    def range_expr(self):

        localctx = RegexParser.Range_exprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_range_expr)
        try:
            self.state = 70
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [RegexParser.T__12]:
                localctx = RegexParser.NegativeSetContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 62
                self.match(RegexParser.T__12)
                self.state = 63
                self.range_item(0)
                self.state = 64
                self.match(RegexParser.T__13)
                pass
            elif token in [RegexParser.T__14]:
                localctx = RegexParser.PositiveSetContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 66
                self.match(RegexParser.T__14)
                self.state = 67
                self.range_item(0)
                self.state = 68
                self.match(RegexParser.T__13)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class Range_itemContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_range_item

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class SingleCharContext(Range_itemContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.Range_itemContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def char(self):
            return self.getTypedRuleContext(RegexParser.CharContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSingleChar" ):
                return visitor.visitSingleChar(self)
            else:
                return visitor.visitChildren(self)


    class ConcatRangeItemContext(Range_itemContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.Range_itemContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def range_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RegexParser.Range_itemContext)
            else:
                return self.getTypedRuleContext(RegexParser.Range_itemContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConcatRangeItem" ):
                return visitor.visitConcatRangeItem(self)
            else:
                return visitor.visitChildren(self)


    class CharRangeContext(Range_itemContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.Range_itemContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def char(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(RegexParser.CharContext)
            else:
                return self.getTypedRuleContext(RegexParser.CharContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCharRange" ):
                return visitor.visitCharRange(self)
            else:
                return visitor.visitChildren(self)



    def range_item(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = RegexParser.Range_itemContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 8
        self.enterRecursionRule(localctx, 8, self.RULE_range_item, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                localctx = RegexParser.CharRangeContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 73
                self.char()
                self.state = 74
                self.match(RegexParser.T__15)
                self.state = 75
                self.char()
                pass

            elif la_ == 2:
                localctx = RegexParser.SingleCharContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 77
                self.char()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 84
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,6,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = RegexParser.ConcatRangeItemContext(self, RegexParser.Range_itemContext(self, _parentctx, _parentState))
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_range_item)
                    self.state = 80
                    if not self.precpred(self._ctx, 3):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                    self.state = 81
                    self.range_item(4) 
                self.state = 86
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,6,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class DigitsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_digits

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ManyDigitsContext(DigitsContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.DigitsContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def Digit(self, i:int=None):
            if i is None:
                return self.getTokens(RegexParser.Digit)
            else:
                return self.getToken(RegexParser.Digit, i)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitManyDigits" ):
                return visitor.visitManyDigits(self)
            else:
                return visitor.visitChildren(self)



    def digits(self):

        localctx = RegexParser.DigitsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_digits)
        self._la = 0 # Token type
        try:
            localctx = RegexParser.ManyDigitsContext(self, localctx)
            self.enterOuterAlt(localctx, 1)
            self.state = 88 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 87
                self.match(RegexParser.Digit)
                self.state = 90 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==RegexParser.Digit):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CharContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return RegexParser.RULE_char

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class CharacterContext(CharContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.CharContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def anyChar(self):
            return self.getTypedRuleContext(RegexParser.AnyCharContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCharacter" ):
                return visitor.visitCharacter(self)
            else:
                return visitor.visitChildren(self)


    class EscapedContext(CharContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a RegexParser.CharContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EscapedChar(self):
            return self.getToken(RegexParser.EscapedChar, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEscaped" ):
                return visitor.visitEscaped(self)
            else:
                return visitor.visitChildren(self)



    def char(self):

        localctx = RegexParser.CharContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_char)
        try:
            self.state = 94
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [RegexParser.EscapedChar]:
                localctx = RegexParser.EscapedContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 92
                self.match(RegexParser.EscapedChar)
                pass
            elif token in [RegexParser.Digit, RegexParser.Punctuation, RegexParser.Letter]:
                localctx = RegexParser.CharacterContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 93
                self.anyChar()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AnyCharContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Punctuation(self):
            return self.getToken(RegexParser.Punctuation, 0)

        def Letter(self):
            return self.getToken(RegexParser.Letter, 0)

        def Digit(self):
            return self.getToken(RegexParser.Digit, 0)

        def getRuleIndex(self):
            return RegexParser.RULE_anyChar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAnyChar" ):
                return visitor.visitAnyChar(self)
            else:
                return visitor.visitChildren(self)




    def anyChar(self):

        localctx = RegexParser.AnyCharContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_anyChar)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 96
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << RegexParser.Digit) | (1 << RegexParser.Punctuation) | (1 << RegexParser.Letter))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.re_sempred
        self._predicates[4] = self.range_item_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def re_sempred(self, localctx:ReContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 1)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 3)
         

    def range_item_sempred(self, localctx:Range_itemContext, predIndex:int):
            if predIndex == 5:
                return self.precpred(self._ctx, 3)
         




