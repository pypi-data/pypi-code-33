#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import sys
import os
from time import strftime
import argparse
import json
import mcafeesecure_api as ms
import pandas as pd
from pandas.io.json import json_normalize

def main():

    # initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vuln_id", help="7 Digit Vulnerability ID")
    parser.add_argument("-m", "--method", help="Chosen API Method: scan-targets, scan-target, scan-result, scan-vuln, full-report")
    parser.add_argument("-t", "--target_id", help="5 Digit Target ID")
    parser.add_argument("-s", "--scan_id", help="32 Character Alphanumeric Scan ID")

    # read arguments from the command line
    args = parser.parse_args()

    # get current data and time
    current_time = strftime('%Y-%m-%d-%H-%M')

    if args.method == 'scan-targets':

        # Retrieve the JSON request
        parsed = json.loads(ms.scan_targets())

        # Flatten and Format JSON into pandas DataFrame
        results = json_normalize(data=parsed['targets'])

        # Generate CSV File
        results.to_csv(args.method + '-' + current_time + '.csv')

    elif args.method == 'scan-target' \
            and len(args.target_id) == 5 and args.target_id.isdigit():

        # Retrieve the JSON request
        parsed = json.loads(ms.scan_target(args.target_id))

        # Flatten and Format JSON into pandas DataFrame
        results = json_normalize(data=parsed['target'])

        # Generate CSV File
        results.to_csv(args.target_id + '-' + args.method + '-' + current_time + '.csv')

    elif args.method == 'scan-result' \
            and len(args.target_id) == 5 and args.target_id.isdigit() \
            and len(args.scan_id) == 32 and args.scan_id.isalnum():

        # Retrieve the JSON request
        parsed = json.loads(ms.scan_result(args.target_id, args.scan_id))

        # Flatten and Format JSON into pandas DataFrame
        parsed_scan = parsed['scan']
        parsed_vulns = parsed_scan['vulns']
        parsed_ports = parsed_scan['ports']
        vuln_results = json_normalize(data=parsed_vulns)
        port_results = json_normalize(data=parsed_ports)
        results = pd.concat([vuln_results, port_results], axis=1)

        # Generate CSV File
        results.to_csv(args.target_id + '-' + args.method + '-' + current_time + '.csv')

    elif args.method == 'scan-vuln' \
            and len(args.vuln_id) == 7 and args.vuln_id.isdigit():

        # Retrieve the JSON request
        parsed = json.loads(ms.scan_vuln(args.vuln_id))

        # Flatten and Format JSON into pandas DataFrame
        results = json_normalize(data=parsed['vuln'])

        # Generate CSV File
        results.to_csv(args.vuln_id + '-' + args.method + '-' + current_time + '.csv')

    elif args.method == 'full-report':
        
        print("Generating report. This may take a few moments...")

        # Retrieve the JSON request
        parsed_targets = json.loads(ms.scan_targets())

         # Flatten and Format JSON into pandas DataFrame
        scan_targets_data = json_normalize(data=parsed_targets['targets'])

        # Create dictionaries relating the targetId parameter to important data
        hostname_dict = dict(zip(scan_targets_data['targetId'], scan_targets_data['hostname']))
        name_dict = dict(zip(scan_targets_data['targetId'], scan_targets_data['name']))
        scan_dict = dict(zip(scan_targets_data['lastScan.scanId'],scan_targets_data['targetId']))

        # Create a general DataFrame to hold report data
        df = pd.DataFrame()

        # Parse the last scan for ever target for report data
        for scan_id, target_id in scan_dict.items():

            # Logical check for NaN values since NaN != NaN
            if scan_id == scan_id:
                # Retrieve the JSON request
                parsed = json.loads(ms.scan_result(target_id, scan_id))

                # Flatten and Format JSON into pandas DataFrame
                parsed_scan = parsed['scan']
                temp_vuln_data = json_normalize(data=parsed_scan['vulns'])

                # Add new column data to the existing scan_result report
                temp_vuln_data['hostname'] = hostname_dict[target_id]
                temp_vuln_data['portalname'] = name_dict[target_id]

                # Add scan data to DataFrame and move to the next scan
                df = df.append(temp_vuln_data, ignore_index=True, sort=False)


        # Create a set of all VulnIds for no repetition
        vuln_id_set = set(df['vulnId'].tolist())

        # Create a vulnerability specific DataFrame 
        vuln_df = pd.DataFrame()

        # Step through each vuln and gather information and add it to Vuln DataFrame
        for vuln in vuln_id_set:
            # Retrieve the JSON request
            parsed_vuln = json.loads(ms.scan_vuln(int(vuln)))

            # Flatten and Format JSON into pandas DataFrame
            parsed_vuln = json_normalize(data=parsed_vuln['vuln'])

            # Add the vulnerabiliy information do the Vuln DataFrame
            vuln_df = vuln_df.append(parsed_vuln, ignore_index=True, sort=False)

        # Perform a merge on the main DataFrame with the VulnDataFrame upon the vulnID field
        results = pd.merge(df, vuln_df[['vulnId', 'name', 'category', 'description', 'solution']], on='vulnId')
        

        # Generate CSV File
        results.to_csv(args.method + '-' + current_time + '.csv') 
        print("Report created. It may be found at " + os.path.dirname(os.path.abspath(__file__))) 


    else:
        print('Error: Unexpected Parameters')
        return


if __name__ == '__main__':
    main()
