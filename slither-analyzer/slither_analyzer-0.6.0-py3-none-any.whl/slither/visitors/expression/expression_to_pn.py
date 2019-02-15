
from slither.visitors.expression.expression import ExpressionVisitor

def get(expression):
    val = expression.context['ExpressionPrinter']
    # we delete the item to reduce memory use
    del expression.context['ExpressionPrinter']
    return val

def set_val(expression, val):
    expression.context['ExpressionPrinter'] = val

class ConvertToPN(ExpressionVisitor):

    @staticmethod
    def _flat(l):
        return [item for sublist in l for item in sublist]

    def result(self):
        if not self._result:
            self._result = get(self.expression)
        return self._result

    def _post_assignement_operation(self, expression):
        left = get(expression.expression_left)
        right = get(expression.expression_right)
#        val = "{} {} {}".format(left, expression.type_str, right)
        val = [left, right, [expression.type_str]]
        val = self._flat(val)
#        val = [item for sublist in val for item in sublist]
        set_val(expression, val)

    def _post_binary_operation(self, expression):
        left = get(expression.expression_left)
        right = get(expression.expression_right)
        val = [left, right,  [expression.type_str]]
        #val = "{} {} {}".format(left,  expression.type_str, right)
        val = self._flat(val)
        set_val(expression, val)

    def _post_call_expression(self, expression):
        called = get(expression.called)
        arguments = [get(x) for x in expression.arguments if x]
        #val = "{}({})".format(called, ','.join(arguments))o
        args = []
        val = []
        for argument in arguments:
            argument = self._flat(argument)
            val += argument
            args += ['ARG']
        val += called
        val += ['CALL{}'.format(len(arguments))]
        val += args
#        val = self._flat(val)
        set_val(expression, val)

    def _post_conditional_expression(self, expression):
        if_expr = get(expression.if_expression)
        else_expr = get(expression.else_expression)
        then_expr = get(expression.then_expression)
        val = "if {} then {} else {}".format(if_expr, else_expr, then_expr)
        
#        val = self._flat(val)
        set_val(expression, val)

    def _post_elementary_type_name_expression(self, expression):
        set_val(expression, [expression.type])

    def _post_identifier(self, expression):
        set_val(expression, [expression.value])

    def _post_index_access(self, expression):
        left = get(expression.expression_left)
        right = get(expression.expression_right)
#        val = "{}[{}]".format(left, right)
        val = [left, right, ['[]']]
        val = self._flat(val)
        set_val(expression, val)

    def _post_literal(self, expression):
        set_val(expression, [expression.value])

    def _post_member_access(self, expression):
        expr = get(expression.expression)
        member_name = expression.member_name
#        val = "{}.{}".format(expr, member_name)
        val = [[member_name], expr, ['->']]
        val = self._flat(val)
        set_val(expression, val)

    def _post_new_array(self, expression):
        array = expression.array_type
        depth = expression.depth
        #val = "new {}{}".format(array, '[]'*depth)
        val = [array, depth, 'NEW_ARRAY']
        set_val(expression, val)

    def _post_new_contract(self, expression):
        contract = expression.contract_name
        #val = "new {}".format(contract)
        val = [contract, ['NEW_CONTRACT']]
        val = self._flat(val)
        set_val(expression, val)

    def _post_new_elementary_type(self, expression):
        t = expression.type
#        val = "new {}".format(t)
        val = [t, 'NEW_ELEMENTARY_TYPE']
        set_val(expression, val)

    def _post_tuple_expression(self, expression):
        expressions = [get(e) for e in expression.expressions if e]
        #val = "({})".format(','.join(expressions))
        val = self._flat(expressions)
        set_val(expression, expressions)

    def _post_type_conversion(self, expression):
        t = expression.type
        expr = get(expression.expression)
#        val = "{}({})".format(t, expr)
        val = [expr, [t], ['CONVERT']]
        val = self._flat(val)
        set_val(expression, val)

    def _post_unary_operation(self, expression):
        t = str(expression.type)
        expr = get(expression.expression)
        if expression.is_prefix:
            val = [[t], expr]
#            val = "{}{}".format(t, expr)
        else:
            val = [expr, [t]]
 #           val = "{}{}".format(expr, t)
        val = self._flat(val)
        set_val(expression, val)
