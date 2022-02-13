#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2020, One Identity LLC
# File: pmjoin.py
# Desc: Ansible module that wraps pmjoin join/unjoin commands.
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
module: pmjoin

short_description: Active Directory join

version_added: '2.9'

description: >
    Performs policy server join/unjoin using the Privilege Manager pmjoin binary.

options:
    state:
        description:
            - Policy server join state
        type: str
        required: false
        default: joined
        choices: ['joined', 'unjoined']
    server:
        description:
            - Policy server to use for join
        type: str
        required: true
    password:
        description:
            - Policy server join password
        type: str
        required: true
    extra_args:
        description:
            - Other arguments to be passed on to vastool
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
        default: 'vastool_join'

author:
    - Mark Stillings (mark.stillings@oneidentity.com)
"""

EXAMPLES = """
- name: Simple join
  pmjoin:
    state: joined
    server: policy1
    password: pass
  register: pmjoin_result
- name: Simple unjoin
  pmjoin:
    state: unjoined
    server: policy1
    password: pass
  register: pmjoin_result
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
            description: Version of pmjoin
            type: str
            returned: always
        output:
            description: pmjoin join/unjoin output
            type: str
            returned: when facts_verbose true
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
import sys
import subprocess
import traceback
import re
import ansible_collections.oneidentity.privilege_manager.plugins.module_utils.pmjoin as pmj


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg choices and defaults
STATE_DEFAULT = 'joined'
STATE_CHOICES = ['joined', 'unjoined']
EXTRA_ARGS_DEFAULT = ''
FACTS_DEFAULT = True
FACTS_VERBOSE_DEFAULT = True
FACTS_KEY_DEFAULT = 'pmjoin'


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
            'state': {
                'type': 'str',
                'required': False,
                'choices': STATE_CHOICES,
                'default': STATE_DEFAULT
            },
            'server': {
                'type': 'str',
                'required': True
            },
            'password': {
                'type': 'str',
                'required': True,
                'no_log': True
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
        supports_check_mode=False
    )

    # Run logic
    # NOTE: This module does not support check mode right now so no special check handling
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
    changed = False
    output = ''

    # Parameters
    state = params['state']
    server = params['server']
    password = params['password']
    extra_args = params['extra_args']
    facts = params['facts']
    facts_verbose = params['facts_verbose']
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT

    try:

        # Check pmjoin
        err, pmjoin_path, pminfo_path, pmjoin_version = pmj.pmjoin_find()

        # Run pmjoin
        if err is None:
            err, changed, output = run_pmjoin(
                pmjoin_path,
                state,
                server,
                password,
                extra_args)

    except Exception:
        tb = traceback.format_exc()
        err = str(tb)

    # Build result
    result['changed'] = changed
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''

    # Create ansible_facts data
    if facts:
        result_facts = result.copy()
        result_facts['params'] = params
        result_facts['path'] = pmjoin_path
        result_facts['version'] = pmjoin_version
        if facts_verbose:
            result_facts['output'] = output
        result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


# ------------------------------------------------------------------------------
def run_pmjoin(
        path,
        state,
        server,
        password,
        extra_args):
    """
    Run pmjoin
    """

    # Return values
    err = None
    changed = False
    output = ''

    # Check status to decide what to do
    status_server = pmj.pmjoin_status()

    # Joined
    if state == 'joined':

        # If not already joined to a domain then join
        if status_server is None:
            err, changed, output = run_pmjoin_join(
                path,
                server,
                password,
                extra_args
            )

        # If already joined to requested domain then do nothing
        else:
            output = 'Already joined to server'

    # Unjoined
    elif state == 'unjoined':

        # If joined to a domain then unjoin
        if status_server is not None:
            err, changed, output = run_pmjoin_unjoin(
                path,
                extra_args
            )

        # If already unjoined then do nothing
        else:
            output = 'Already unjoined from server'

    # Unknown state
    else:
        err = 'Unexpected state requested: ' + state

    # Return
    return err, changed, output


# ------------------------------------------------------------------------------
def run_pmjoin_join(
        path,
        server,
        password,
        extra_args):

    # Return values
    err = None
    changed = False
    output = ''

    # Build vastool command
    cmd = []
    cmd += [path]
    cmd += ['-b']
    cmd += ['-a']
    cmd += ['-q']
    cmd += [server]
    cmd += [extra_args] if extra_args else []

    # Call vastool
    try:
        p = subprocess.Popen(' '.join(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        rval_bytes, rval_err = p.communicate(password.encode(sys.stdout.encoding))
        rval_bytes += rval_err
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    # Popen returns list of bytes so we have to decode to get a string
    rval_str = rval_bytes.decode(sys.stdout.encoding)

    # Parse pmjoin return
    err, changed, output = parse_pmjoin_output(rval_str)

    # Return
    return err, changed, output


# ------------------------------------------------------------------------------
def run_pmjoin_unjoin(
        path,
        extra_args):

    # Return values
    err = None
    changed = False
    output = ''

    # Build vastool command
    cmd = []
    cmd += [path]
    cmd += ['-b']
    cmd += ['-a']
    cmd += ['-u']
    cmd += [extra_args] if extra_args else []

    # Call vastool
    try:
        p = subprocess.Popen(' '.join(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        rval_bytes, rval_err = p.communicate()
        rval_bytes += rval_err
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    # Popen returns list of bytes so we have to decode to get a string
    rval_str = rval_bytes.decode(sys.stdout.encoding)

    # Parse pmjoin return
    err, changed, output = parse_pmjoin_output(rval_str)

    # Return
    return err, changed, output


# ------------------------------------------------------------------------------
def parse_pmjoin_output(output_str):

    # Return values
    err = None
    changed = False
    output = output_str

    # Find errors
    error_re_str = r'^(.*\b(FAIL|ERROR)\b.*)$'
    error_re = re.compile(error_re_str, re.MULTILINE | re.IGNORECASE)
    error_re_match = error_re.findall(output_str)

    # Build list of errors
    err_list = []
    for error_match in error_re_match:
        err_list += [error_match[0].replace('*', '').strip()]

    # If no errors then we succeeded, mark changed
    if not err_list:
        changed = True

    # Check for error
    if err_list:
        err = '\n'.join(err_list)

    # Return
    return err, changed, output


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
