
from slither.visitors.expression.expression import ExpressionVisitor
from slither.core.expressions import SuperIdentifier

class FindSuperIdentifier(ExpressionVisitor):

    def result(self):
        if not self._result:
            return []
        return self._result

    def _post_identifier(self, expression):
        if isinstance(expression, SuperIdentifier):
            if not self._result:
                self._result = []
            self._result.append(expression.value)
