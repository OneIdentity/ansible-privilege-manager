#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2020, One Identity LLC
# File: preflight.py
# Desc: Ansible module for client_join role that performs Active Directory
#       pre-join checking by using the Authentication Services preflight
#       binary.
# Auth: Mark Stillings
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
module: preflight

short_description: Active Directory pre-join checking

version_added: '2.9'

description: >
    Performs Privilege Manager software pre-install and pre-join checking by
    using the Privilege Mananger preflight binary.

options:
    mode:
        description:
            - preflight mode
        type: str
        required: true
        choices: ['server', 'pmpolicy', 'sudo']
    server:
        description:
            - Policy server
        type: str
        required: false
        default: ''
    verbose:
        description:
            - Verbose
        type: bool
        required: false
        default: False
    extra_args:
        description:
            - Other arguments to be passed on to preflight
        type: str
        required: false
        default: ''
    facts:
        description:
            - Generate Ansible facts?
        type: bool
        required: false
        default: true
    facts_verbose:
        description:
            - Verbose Ansible facts?
        type: bool
        required: false
        default: true
    facts_key:
        description:
            - Ansible facts key
        type: str
        required: false
        default: 'preflight'
    path:
        description:
            - Path to preflight binary
        type: str
        required: false
        default: /opt/quest/bin/preflight

author:
    - Mark Stillings (mark.stillings@oneidentity.com)
"""

EXAMPLES = """
- name: Normal usage
  preflight:
    domain: oneidentity.com
    username: user
    password: pass
  register: preflight_result
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
        version:
            description: Version of preflight
            type: str
            returned: always
        steps:
            description: The preflight checks and results of those checks
            type: list of dicts
            returned: when facts_verbose true
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
import sys
import subprocess
import ansible_collections.oneidentity.privilege_manager.plugins.module_utils.check_file_exec as cfe


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg defaults
SERVER_DEFAULT = ''
VERBOSE_DEFAULT = False
EXTRA_ARGS_DEFAULT = ''
PATH_DEFAULT = '/tmp/1id/pmpreflight'
FACTS_DEFAULT = True
FACTS_VERBOSE_DEFAULT = True
FACTS_KEY_DEFAULT = 'preflight'
MODE_CHOICES = ['server', 'pmpolicy', 'sudo']


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
            'mode': {
                'type': 'str',
                'required': True,
                'choices': MODE_CHOICES
            },
            'server': {
                'type': 'str',
                'required': False,
                'default': SERVER_DEFAULT
            },
            'verbose': {
                'type': 'bool',
                'required': False,
                'default': VERBOSE_DEFAULT
            },
            'extra_args': {
                'type': 'str',
                'required': False,
                'default': EXTRA_ARGS_DEFAULT
            },
            'facts': {
                'type': 'bool',
                'required': False,
                'default': FACTS_DEFAULT
            },
            'facts_verbose': {
                'type': 'bool',
                'required': False,
                'default': FACTS_VERBOSE_DEFAULT
            },
            'facts_key': {
                'type': 'str',
                'required': False,
                'default': FACTS_KEY_DEFAULT
            },
            'path': {
                'type': 'str',
                'required': False,
                'default': PATH_DEFAULT
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
    steps = []

    # Parameters
    mode = params['mode']
    server = params['server']
    verbose = params['verbose']
    extra_args = params['extra_args']
    facts = params['facts']
    facts_verbose = params['facts_verbose']
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT
    path = params['path'] if params['path'] else PATH_DEFAULT

    # Check preflight
    err, version = cfe.check_file_exec(path, '-v')

    # Run preflight
    if err is None:
        err, steps = run_preflight(
            mode,
            server,
            verbose,
            extra_args,
            path)

    # Build result
    result['changed'] = False   # preflight never makes any changes to the host
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''

    # Create ansible_facts data
    if facts:
        result_facts = result.copy()
        result_facts['params'] = params
        result_facts['version'] = version
        if facts_verbose:
            result_facts['steps'] = steps
        result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


# ------------------------------------------------------------------------------
def run_preflight(
        mode,
        server,
        verbose,
        extra_args,
        path):
    """
    Run preflight
    """

    # Return values
    err = None
    steps = []

    # Build preflight command
    cmd = []
    cmd += [path]
    cmd += ['--' + mode]
    cmd += ['--policyserver ' + server] if server and mode in MODE_CHOICES[1:] else []
    cmd += ['--verbose'] if verbose else []
    cmd += ['--csv']
    cmd += [extra_args] if extra_args else []

    # Call preflight
    try:
        rval_bytes = subprocess.check_output(' '.join(cmd), stderr=subprocess.STDOUT, shell=True)
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    # check_output returns list of bytes so we have to decode to get a string
    rval_str = rval_bytes.decode(sys.stdout.encoding)

    # Parse preflight return
    err, steps = parse_preflight_steps(rval_str)

    # Return
    return err, steps


# ------------------------------------------------------------------------------
def parse_preflight_steps(steps_str):

    # Return values
    err = None
    steps = []

    results = {
            0: 'Pass',
            1: 'Warning',
            2: 'Failure',
            255: 'Skipped'
        }
    for step_line in steps_str.splitlines():
        step_items = step_line.split(',')
        if len(step_items) > 4:
            steps += [
                {
                    'description': step_items[2].strip().replace("\"", ""),
                    'message': ', '.join(filter(None, (step_item.strip().replace("\"", "") for step_item in step_items[3:] if step_item.strip()))),
                    'result': results[int(step_items[0])] if int(step_items[0]) in results else int(step_items[0])
                }
            ]

    # Build list of errors
    err_list = []
    for step in steps:
        if step['result'] == 'Failure' and len(step['message']) > 0:
            err_list += [step['result'] + ': ' + step['message']]

    # Check for error
    if err_list:
        err = '\n'.join(err_list)

    # Return
    return err, steps


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
