import pandas as pd

from .utils import get_boto_session


def _run_query(client, query, database, s3_output):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database},
        ResultConfiguration={"OutputLocation": s3_output},
    )
    return response["QueryExecutionId"]


def _query_validation(client, query_exec):
    resp = ["FAILED", "SUCCEEDED", "CANCELLED"]
    response = client.get_query_execution(QueryExecutionId=query_exec)
    while response["QueryExecution"]["Status"]["State"] not in resp:
        response = client.get_query_execution(QueryExecutionId=query_exec)
    return response


def read(
    database,
    query,
    s3_output=None,
    region=None,
    key=None,
    secret=None,
    profile_name=None,
):
    """
    Read any Glue object through the AWS Athena
    """
    session = get_boto_session(
        key=key, secret=secret, profile_name=profile_name, region=region
    )
    if not s3_output:
        account_id = session.client("sts").get_caller_identity().get("Account")
        session_region = session.region_name
        s3_output = (
            "s3://aws-athena-query-resul-" + account_id + "-" + session_region + "/"
        )
        s3 = session.resource("s3")
        s3.Bucket(s3_output)
    athena_client = session.client("athena")
    qe = _run_query(athena_client, query, database, s3_output)
    validation = _query_validation(athena_client, qe)
    if validation["QueryExecution"]["Status"]["State"] == "FAILED":
        message_error = (
            "Your query is not valid: "
            + validation["QueryExecution"]["Status"]["StateChangeReason"]
        )
        raise Exception(message_error)
    else:
        file = s3_output + qe + ".csv"
        df = pd.read_csv(file)
    return df
