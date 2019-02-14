import pyjq
from snucovery.cli import Arguments
from snucovery.aws import AwsServices
from snucovery.excel import ExcelWorkbooks


def main():
    # Get arguments passed from the command line
    args = Arguments().get_args()

    # Instantiate an Aws session based on the profile name
    aws = AwsServices(args.profile)

    # Scan all services that are specified in aws.service_mappings
    items = aws.scan_services()

    # Create a new workbook based on the workbook name
    excel = ExcelWorkbooks(args.workbook_name)

    service_mappings = aws.get_service_mappings()

    # Iterate through the aws service mappings
    for service in service_mappings:
        for service_attr, jq_filter in service_mappings[service].items():
            # Format the service_attr into something more appealing since this
            # is used for setting the worksheets name
            service_name = service_attr.replace('describe_', '').replace('_', ' ')
            excel.create_worksheet(service_name)

            # Leverage `pyjq` to iterate through a valid aws service response
            # and parse the details into what we need.  `jq_filter` should be
            # a valid `jq` filter string
            filtered_items = pyjq.all(jq_filter, items[service][service_attr])
            try:
                excel.create_headers_from_dict(service_name, filtered_items[0])
                excel.add_rows_to_worksheet_from_json(service_name, filtered_items)
            except IndexError:
                pass

    excel.close()


if __name__ == '__main__':
    main()
