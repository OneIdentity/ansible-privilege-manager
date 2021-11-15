#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2021, One Identity LLC
# File: get_sudo_policy_for_unix_host.py
# Desc: Ansible module for sudo_policy_for_unix_host role that runs pmsrvinfo
#       and returns its results.
# Auth: Laszlo Nagy
# Note:
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Required Ansible documentation
# ------------------------------------------------------------------------------

ANSIBLE_METADATA = {
    'metadata_version': '0.2',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = """
---
module: get_sudo_policy_for_unix_host.py

short_description: >
    Returns the sudo policy in use

version_added: '2.9'

description: >
    Returns the version of Privilege Manager for sudo plugins and the sudo policies in use

options:
    facts:
        description:
            - Generate Ansible facts?
        type: bool
        required: false
        default: true
    facts_key:
        description:
            - Ansible facts key
        type: str
        required: false
        default: 'sudo_policy_for_unix_host'

author:
    - Laszlo Nagy (laszlo.nagy@oneidentity.com)
"""

EXAMPLES = """
- name: Normal usage
  get_sudo_policy_for_unix_host:
    facts: true
  register: get_sudo_policy_for_unix_host_result
"""

RETURN = """
ansible_facts:
    description: All non-standard return values are placed in Ansible facts
    type: dict
    returned: when facts parameter is true
    keys:
        changed:
            description: Did the state of the host change?
            type: bool
            returned: always
        failed:
            description: Did the module fail?
            type: bool
            returned: always
        msg:
            description: Additional information if failed
            type: str
            returned: always
        params:
            description: Parameters passed in
            type: dict
            returned: always
        sudo_policy_for_unix_host:
            description: hostname, policy plugin, version and timestamp of each host
            type: list of lists
            returned: always
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from io import StringIO
import csv
import platform
import subprocess
import sys
import traceback
import ansible_collections.oneidentity.authentication_services.plugins.module_utils.vastool as vt
import ansible_collections.oneidentity.authentication_services.plugins.module_utils.check_file_exec as cfe


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg defaults
FACTS_DEFAULT = True
FACTS_KEY_DEFAULT = 'sudo_policy_for_unix_host'

PMSRVINFO_PATH = '/opt/quest/sbin/pmsrvinfo'

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
def run_module():
    """
    Main Ansible module function
    """

    # Module argument info
    module_args = {
            'facts': {
                'type': 'bool',
                'required': False,
                'default': FACTS_DEFAULT
            },
            'facts_key': {
                'type': 'str',
                'required': False,
                'default': FACTS_KEY_DEFAULT
            }
        }

    # Seed result value
    result = {
            'changed': False,
            'failed': False,
            'msg': ''
        }

    # Lean on boilerplate code in AnsibleModule class
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Run logic
    # NOTE: This module makes no changes so check mode doesn't need to be handled
    #       specially
    err, result = run_normal(module.params, result)

    # Exit
    module.exit_json(**result)


# ------------------------------------------------------------------------------
def run_normal(params, result):
    """
    Normal mode logic.

    params contains input parameters.

    result contains run results skeleton, will modify/add to and then return
    this value along with an err value that contains None if no error or a string
    describing the error.
    """

    # Return data
    err = None
    version = ''
    sudo_policies = []

    # Parameters
    facts = params['facts']
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT

    try:

        while True:
            err, version = cfe.check_file_exec(PMSRVINFO_PATH, '')
            if err is not None:
                break

            err, sudo_policies = run_pmsrvinfo()
            if err is not None:
                break

            break

    except Exception:
        tb = traceback.format_exc()
        err = str(tb)

    # Build result
    result['changed'] = False   # this module never makes any changes to the host
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''

    # Create ansible_facts data
    if facts:
        result_facts = result.copy()
        result_facts['params'] = params
        result_facts['sudo_policy_for_unix_host'] = sudo_policies
        result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


# ------------------------------------------------------------------------------
def run_pmsrvinfo():

    # Return values
    err = None
    sudo_policies = []

    # Build pmsrvinfo command
    cmd = []
    cmd += [PMSRVINFO_PATH]
    cmd += ['-l']
    cmd += ['-c']

    # Call asdcom
    try:
        p = subprocess.Popen(' '.join(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        rval_bytes, rval_err = p.communicate()
        rval_bytes += rval_err
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    if p.returncode == 0:
        # Popen returns list of bytes so we have to decode to get a string
        rval_str = rval_bytes.decode(sys.stdout.encoding)

        # Parse pmsrvinfo return
        err, sudo_policies = parse_pmsrvinfo_stdout(rval_str)

    # Return
    return err, sudo_policies


# ------------------------------------------------------------------------------
def parse_pmsrvinfo_stdout(stdout_str):
    """
    Example result:
    $ /opt/quest/sbin/pmsrvinfo -l -c
    qpm-rhel6-64d,/etc/opt/quest/qpm4u/policy/sudoers,7.1.99.7-55-g787b0a37e,1634124307
    qpm-rhel6-64c,/etc/opt/quest/qpm4u/policy/sudoers,7.1.99.10-6-g8c6b6955d,1634124308
    """

    # Return values
    err = None
    sudo_policies = []

    text_stream = StringIO(stdout_str)
    csv_reader = csv.reader(text_stream)
    for row in csv_reader:
        sudo_policies.append([ row[0], row[1], row[2], row[3] ])

    # Return
    return err, sudo_policies


# ------------------------------------------------------------------------------
def main():
    """
    Main
    """

    run_module()


# When run from command line
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
