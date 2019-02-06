"""Adapted from Hello Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import numpy as np

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']


def initialize_analyticsreporting(key_file_location):
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
        An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        key_file_location, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, view_id, start_date, end_date, metrics, dimensions):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
        The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(body={
        'reportRequests': [{
            'viewId': view_id,
            'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
            'metrics': [{'expression': m} for m in metrics],
            'dimensions': [{'name': d} for d in dimensions]
        }]
    }).execute()


def parse_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
        response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        report_rows = []
        for row in report.get('data', {}).get('rows', []):
            report_row = {}
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                report_row[header] = dimension
                #print(header + ': ' + dimension)

            # we ignore other date ranges so we slice the first one
            for i, values in list(enumerate(dateRangeValues))[0:1]:
                #print('Date range: ' + str(i))
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    report_row[metricHeader.get('name')] = value
                    #print(metricHeader.get('name') + ': ' + value)

            report_rows.append(report_row)

        # the return is in the first loop as we only want one report
        return pd.DataFrame(report_rows)


def read_ga(key_file, view_id, start_date, end_date, metrics, dimensions=[]):
    analytics = initialize_analyticsreporting(key_file)
    response = get_report(analytics, view_id, start_date, end_date, metrics, dimensions)
    return parse_response(response)


if __name__ == '__main__':
    pass