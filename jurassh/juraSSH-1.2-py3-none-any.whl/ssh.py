#!/usr/bin/env python

import paramiko
import time

__author__ = "David Johnnes"
__email__ = "david.johnnes@gmail.com"

"""This module can be used to establish SSH connection to any devices that supports SSH.

    # For single command execution, you should use the "send_single_command() function"
    # for multiple commands execution you should use the send_multiple_commands() function
"""


def send_single_command(hostname, user_name, pass_word, command,
                        key=False, timeout=10, port=22, sleep_time=2):
    """ Send a single command to a remote machine.

        :command must be a string data type
        :The output of the command will be printed
        :return 'The output of the command will be returned'
    """

    ssh = paramiko.SSHClient()

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, port=port, username=user_name,
                    password=pass_word, look_for_keys=key, timeout=timeout)
        print("Connected to {0}\n".format(hostname))

    except:
        print("Could not connect to {0}".format(hostname))
        ssh.close()
    else:
        channel = ssh.invoke_shell()

        channel.send(command + "\n")
        time.sleep(2)

        output = channel.recv(9999)
        time.sleep(sleep_time)

        print(output)
        print("#" * 120)

        channel.close()
        ssh.close()
        return output


def send_multiple_commands(hostname, user_name, pass_word, list_of_commands,
                           key=False, timeout=10, port=22, sleep_time=2):
    """ Send multiple commands to  a remote machine.

        :list_of_commands must be a list data type.
        :The outputs of the list_of_commands will be printed
        :return 'The outputs of the list_of_commands will be returned'
    """

    ssh = paramiko.SSHClient()

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=user_name,
                    password=pass_word, look_for_keys=key, timeout=timeout, port=port)
        print("Connected to {0}\n".format(hostname))

    except:
        print("Could not connect to {0}".format(hostname))
        ssh.close()
    else:
        channel = ssh.invoke_shell()
        channel_data = str()

        for cmd in list_of_commands:

            channel.send(cmd + "\n")
            time.sleep(2)

            output = channel.recv(99999)
            time.sleep(sleep_time)

            channel_data += output
            print(output)
            print("#" * 120)
            print("\n")

        channel.close()
        ssh.close()
        return channel_data



