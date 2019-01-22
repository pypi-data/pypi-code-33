from . import core
from . import aws_lambda


lam = core.l  # boto3 lambda client passthrough
test = aws_lambda.test
create = aws_lambda.create_function
publish = aws_lambda.publish
