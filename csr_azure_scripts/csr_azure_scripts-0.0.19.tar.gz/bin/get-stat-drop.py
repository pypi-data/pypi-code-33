#!/usr/bin/env python
import re
import argparse
import json
import cli

from csr_cloud import meta_utils
from csr_azure_scripts import cas

csr = cas()
logger = csr.logger

csr_metadata = meta_utils.MetaDataUtils()
instanceId = csr_metadata.get_rg_vmname_combo_id()
instanceName = csr_metadata.get_instance_name()

def print_cmd_output(command, output, print_output):
    if print_output:
        col_space = (80 - (len(command))) / 2
        print "\n%s %s %s" % ('=' * col_space, command, '=' * col_space)
        print "%s \n%s" % (output, '=' * 80)


def execute_command(command, print_output):
    cmd_output = cli.execute(command)
    while len(cmd_output) == 0:
        print "CMD FAILED, retrying"
        cmd_output = cli.execute(command)

    print_cmd_output(command, cmd_output, print_output)
    return cmd_output


def get_stat_drop(print_output):
    for i in range(2):
        try:
            cmd_output = execute_command(
                "show platform hardware qfp active statistics drop clear", print_output)

            if "all zero" in cmd_output:
                csr.put_metric("TailDrop", int(0), instanceId, instanceName)
                return

            if "TailDrop" not in cmd_output:
                csr.put_metric("TailDrop", int(0), instanceId, instanceName)

            for line in cmd_output.splitlines():
                if ("-" in line) or ("Global Drop Stats" in line):
                    continue

                entries = line.split()
                print entries
                if print_output:
                    print "%s --> %s/%s" % (entries[0], entries[1], entries[2])
                csr.put_metric(entries[0], int(entries[1]), instanceId, instanceName)
                break
        except Exception as e:
            logger.exception(e)
            pass

def get_datapath_util(print_output):
    cmd_output = execute_command(
        "show platform hardware qfp active datapath utilization", print_output)

    row_names = [
        "input_priority_pps",
        "input_priority_bps",
        "input_non_priority_pps",
        "input_non_priority_bps",
        "input_total_pps",
        "input_total_bps",
        "output_priority_pps",
        "output_priority_bps",
        "output_non_priority_pps",
        "output_non_priority_bps",
        "output_total_pps",
        "output_total_bps",
        "processing_load_pct"]

    i = 0
    for line in cmd_output.splitlines():
        m = re.search(
            r'.*\s+(?P<fivesecs>\d+)\s+(?P<onemin>\d+)\s+(?P<fivemin>\d+)\s+(?P<onehour>\d+)', line)
        if m:
            # print "%s --> %s %s %s %s" % (row_names[i],
            # m.group('fivesecs'),m.group('onemin'),m.group('fivemin'),m.group('onehour'))
            csr.put_metric(row_names[i] + '_fivesecs', m.group('fivesecs'), instanceId, instanceName)
            csr.put_metric(row_names[i] + '_onemin', m.group('onemin'), instanceId, instanceName)
            csr.put_metric(row_names[i] + '_fivemin', m.group('fivemin'), instanceId, instanceName)
            csr.put_metric(row_names[i] + '_onehour', m.group('onehour'), instanceId, instanceName)
            i = i + 1


def show_interface(print_output):
    cmd_output = execute_command("show interface summary", print_output)
    table_start = 0
    for line in cmd_output.splitlines():
        if 'Interface' in line:
            continue
        if "-" in line:
            table_start = 1
            continue
        if table_start == 0:
            continue
        entries = line.lstrip('*').split()
        cmd = "show interface %s" % (entries[0])
        interface_output = execute_command(cmd, print_output)
        m = re.search(
            r'.*\s+(?P<packets_input>\d+) packets input.*\s+(?P<bytes_input>\d+) bytes.*', interface_output)
        if m:
            # print "match! %s %s" %
            # (m.group('packets_input'),m.group('bytes_input'))
            csr.put_metric("packets_input_" + entries[0], m.group('packets_input'), instanceId, instanceName)
            csr.put_metric("bytes_input_" + entries[0], m.group('bytes_input'), instanceId, instanceName)

        m = re.search(
            r'.*\s+(?P<packets_output>\d+) packets output.*\s+(?P<bytes_output>\d+) bytes.*', interface_output)
        if m:
            # print "match! %s %s" %
            # (m.group('packets_output'),m.group('bytes_output'))
            csr.put_metric("packets_output_" + entries[0], m.group('packets_output'), instanceId, instanceName)
            csr.put_metric("bytes_output_" + entries[0], m.group('bytes_output'), instanceId, instanceName)
        m = re.search(
            r'.*\s+(?P<unknown_drops>\d+) unknown protocol drops.*', interface_output)
        if m:
            # print "match! %s" % (m.group('unknown_drops'))
            csr.put_metric("unknown_drops_" + entries[0], m.group('unknown_drops'), instanceId, instanceName)
        m = re.search(
            r'.*Total output drops:\s+(?P<output_drops>\d+)\s+.*', interface_output)
        if m:
            # print "match! %s" % (m.group('output_drops'))
            csr.put_metric("output_drops_" + entries[0], m.group('output_drops'), instanceId, instanceName)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Stats to custom metrics")
    parser.add_argument('--display', help='Show Output', action='store_true')
    parser.add_argument('--category', help='Send ', default="all")

    args = parser.parse_args()

    if args.category in ["all", "drops"]:
        get_stat_drop(args.display)
    if args.category in ["all", "util"]:
        get_datapath_util(args.display)
    if args.category in ["all", "interface"]:
        show_interface(args.display)

    csr.flush_metric_queue()