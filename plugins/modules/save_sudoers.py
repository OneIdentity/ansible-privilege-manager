#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2021, One Identity LLC
# File: save_sudoers.py
# Desc: Ansible module for sudoers role that saves the complete sudoers file on
#       the controller node
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
module: save_sudoers.py

short_description: Saves the sudoers file on the controller node.

version_added: '2.9'

description: >
    Saves the sudoers file on the controller node.

options:
    path:
        description:
            - Path to the output file
        type: str
        required: true
    content:
        description:
            - Content of the output file
        type: str
        required: true
    facts_key:
        description:
            - Ansible facts key
        type: str
        required: false
        default: 'save_sudoers'

author:
    - Laszlo Nagy (laszlo.nagy@oneidentity.com)
"""

EXAMPLES = """
- name: Normal usage
  save_sudoers:
    path: /tmp/1id/hostname/etc/sudoers
    content: "{{ sudoers_content }}"
  register: save_sudoers_result
"""

RETURN = """
ansible_facts:
    description: All non-standard return values are placed in Ansible facts
    type: dict
    returned: always
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
        dest:
            description: Path to complete main sudoers file
            type: str
            returned: always
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes
from ansible.utils.path import makedirs_safe
import os
import traceback

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg defaults
FACTS_KEY_DEFAULT = 'save_sudoers'


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
            'path': {
                'type': 'str',
                'required': True
            },
            'content': {
                'type': 'str',
                'required': True
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

    # Parameters
    sudoers_path = params['path']
    sudoers_content = params['content']
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT

    try:
        sudoers_path = os.path.normpath(sudoers_path)

        # create the containing directories, if needed
        makedirs_safe(os.path.dirname(sudoers_path))

        f = open(to_bytes(sudoers_path, errors='surrogate_or_strict'), 'wb')
        f.write(to_bytes(sudoers_content, errors='surrogate_or_strict'))
        f.close()

    except Exception:
        tb = traceback.format_exc()
        err = str(tb)

    # Build result
    result['changed'] =  True if err is None else False
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''

    # Create ansible_facts data
    result_facts = result.copy()
    result_facts['params'] = params
    result_facts['dest'] = sudoers_path
    result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


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
