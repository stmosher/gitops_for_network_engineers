# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
__author__ = "Steven Mosher <stmosher@cisco.com>"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import os
import paramiko
import re
import sys
import yaml


project_path = os.path.dirname(os.path.realpath(__file__))
username = os.environ.get("USERNAME", "admin")
password = os.environ.get("PASSWORD", "admin")
environment = os.environ.get("ENVIRONMENT", "test")

devices_dict = {"prod": {"prod00": "3.228.97.247",
                         "prod01": "34.192.157.124"},
                "test": {
                    "test00": "18.211.19.45",
                    "test01": "52.21.255.78"
                }}

name_translation = {"prod00": "test00",
                    "prod01": "test01",
                    "test00": "test00",
                    "test01": "test01"}


def prompt(chan):
    """
    Reads SSH data until the prompt is reached.
    """
    buff = ''
    while not buff.endswith('#'):
        r = chan.recv(65535)
        r1 = str(r, 'utf-8')
        buff += r1
    return buff


def device_test(test, ip) -> str:
    """
    Creates SSH connection with device, sends commands, and collects results
    """
    try:
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(ip, port=22, username=username, password=password, look_for_keys=False,
                  allow_agent=False)
        ssh = c.invoke_shell()
        prompt(ssh)
        ssh.send("term length 0 \n")
        prompt(ssh)
        ssh.send(test + "\n")
        output = prompt(ssh)
        ssh.close()
        return output
    except Exception as e:
        print(f'Failed to connect to device {ip}. \nException {e}')
        return False


def check_assertions(result, assertions, device):
    for assertion in assertions:
        if re.search(assertion, result):
            print(f"PASSED - {device}: Assertion '{assertion}'")
        else:
            print(f"FAILED - {device}: Assertion '{assertion}' was not found. Exiting...")
            sys.exit(1)


def run_tests(tests, device):
    for test in tests:
        if environment == "test":
            device = name_translation.get(device)
        result = device_test(test['command'], devices_dict[environment][device])
        check_assertions(result, test['assertions'], device)


def main():
    devices = os.listdir(os.path.join(project_path, "devices"))
    for device in devices:
        device_config_filename = os.path.join(os.path.join(os.path.join(project_path, "devices"), device), "tests.yml")

        with open(device_config_filename, 'r') as yaml_in:
            tests = yaml.safe_load(yaml_in)

        run_tests(tests["tests"], device)


if __name__ == "__main__":
    main()
