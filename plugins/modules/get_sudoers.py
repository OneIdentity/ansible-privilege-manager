#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2021, One Identity LLC
# File: get_sudoers.py
# Desc: Ansible module for sudoers role that returns the list of sudoers files
#       (the main sudoers and all other included sudoers files) and a single
#       complete sudoers file in which all include directives have been replaced
#       by the content of the included files.
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
module: get_sudoers.py

short_description: Returns sudoers files.

version_added: '2.9'

description: >
    Returns the list of sudoers files (the main sudoers and all other
    included sudoers files) and a single complete sudoers file in which
    all include directives have been replaced by the content of the
    included files.

options:
    facts_key:
        description:
            - Ansible facts key
        type: str
        required: false
        default: 'get_sudoers'

author:
    - Laszlo Nagy (laszlo.nagy@oneidentity.com)
"""

EXAMPLES = """
- name: Normal usage
  get_sudoers:
    facts_key: get_sudoers
  register: get_sudoers_result
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
        main_sudoers_path:
            description: Path to main sudoers file
            type: str
            returned: always
        sudoers_files:
            description: List of sudoers files
            type: list of str
            returned: always
        complete_sudoers:
            description: A single complete sudoers file in which all include directives have been replaced by the content of the included files.
            type: bytes
            returned: always
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
import os
import platform
import subprocess
import sys
import traceback


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg defaults
FACTS_KEY_DEFAULT = 'get_sudoers'


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
    sudoers_files = []
    complete_sudoers = b''

    # Parameters
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT

    try:
        err, main_sudoers_path = get_main_sudoers_path()
        if not err:
            lines_of_complete_sudoers = []
            depth = 1
            err = process_sudoers(main_sudoers_path, sudoers_files, lines_of_complete_sudoers, depth)

        if not err:
            complete_sudoers = b''.join(lines_of_complete_sudoers)

    except Exception:
        tb = traceback.format_exc()
        err = str(tb)

    # Build result
    result['changed'] = False   # this module never makes any changes to the host
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''

    # Create ansible_facts data
    result_facts = result.copy()
    result_facts['params'] = params
    result_facts['main_sudoers_path'] = main_sudoers_path
    result_facts['sudoers_files'] = sudoers_files
    result_facts['complete_sudoers'] = complete_sudoers
    result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


# ------------------------------------------------------------------------------
def get_main_sudoers_path():

    # Return values
    err = None
    main_sudoers_path = '/etc/sudoers'

    try:
        p = subprocess.Popen("sudo -V | grep 'Sudoers path:'",
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        rval_bytes, rval_err = p.communicate()
        rval_bytes += rval_err
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    # Popen returns list of bytes so we have to decode to get a string
    rval_str = rval_bytes.decode(sys.stdout.encoding)

    if p.returncode > 0:
        err = rval_str
    else:
        label = 'Sudoers path: '
        if rval_str.startswith(label):
            main_sudoers_path = rval_str[len(label) : ].strip()

    # Return
    return err, main_sudoers_path


# ------------------------------------------------------------------------------
def process_sudoers(sudoers_path, sudoers_files, lines_of_complete_sudoers, depth):

    # Files that are included may themselves include other files. A hard limit
    # of 128 nested include files is enforced to prevent include file loops.
    if depth > 128:
        return 'A hard limit of 128 nested include files is reached!'

    err = None

    sudoers_files.append(sudoers_path)

    sudoers_file = open(sudoers_path, 'rb')
    for line in sudoers_file:
        line_str = to_text(line, errors='surrogate_or_strict')
        line_str = line_str.strip()

        # It is possible to include other sudoers files from within the sudoers
        # file currently being parsed using the @include and @includedir directives.
        # For compatibility with sudo versions prior to 1.9.1, #include and
        # #includedir are also accepted.
        if line_str.startswith('#includedir') or line_str.startswith('@includedir'):
            # The @includedir directive can be used to create a sudoers.d directory
            # that the system package manager can drop sudoers file rules into as
            # part of package installation. For example, given:
            # @includedir /etc/sudoers.d
            # sudo will suspend processing of the current file and read each file
            # in /etc/sudoers.d, skipping file names that end in ‘~’ or contain a
            # ‘.’ character to avoid causing problems with package manager or editor
            # temporary/backup files. Files are parsed in sorted lexical order.
            # Be aware that because the sorting is lexical, not numeric,
            # /etc/sudoers.d/1_whoops would be loaded after
            # /etc/sudoers.d/10_second.
            include_dir = line_str[len('#includedir') : ].strip()
            include_dir = process_include_filename(include_dir)
            include_files = [f for f in os.listdir(include_dir) if os.path.isfile(os.path.join(include_dir, f))]
            if len(include_files) > 0:
                # https://stackoverflow.com/a/7372478
                include_files = sorted(sorted(include_files), key=type(include_files[0]).upper)
                for include_file in include_files:
                    if include_file[-1] == '~':
                        continue
                    if '.' in include_file:
                        continue
                    include_file = os.path.join(include_dir, include_file)
                    err = process_sudoers(include_file, sudoers_files,
                        lines_of_complete_sudoers, depth + 1)
                    if err:
                        break

        elif line_str.startswith('#include') or line_str.startswith('@include'):
            include_file = line_str[len('#include') : ].strip()
            include_file = process_include_filename(include_file)
            if include_file[0] != '/':
                # If the path to the include file is not fully-qualified (does not
                # begin with a ‘/’), it must be located in the same directory as
                # the sudoers file it was included from.
                # For example, if /etc/sudoers contains the line:
                # @include sudoers.local
                # the file that will be included is /etc/sudoers.local.
                dirname = os.path.dirname(sudoers_path)
                include_file = os.path.join(dirname, include_file)
            err = process_sudoers(include_file, sudoers_files,
                lines_of_complete_sudoers, depth + 1)

        else:
            lines_of_complete_sudoers.append(line)

        if err:
            break

    return err


# ------------------------------------------------------------------------------
def process_include_filename(include_file):
    """
    The path to the include file may contain white space if it is escaped with a
    backslash (‘\’).

    Alternately, the entire path may be enclosed in double quotes (""), in which
    case no escaping is necessary.

    To include a literal backslash in the path, ‘\\’ should be used.

    The file name may also include the %h escape, signifying the short form of
    the host name. In other words, if the machine's host name is “xerxes”, then
    @include /etc/sudoers.%h
    will cause sudo to include the file /etc/sudoers.xerxes.
    """

    include_file = include_file.replace('\\\\', '\\')

    if len(include_file) > 2:
        if include_file[0] == '"' and include_file[-1] == '"':
            include_file = include_file[1 : -1]
        else:
            include_file = include_file.replace('\\ ', ' ')

    if '%h' in include_file:
        hostname = platform.uname()[1]
        include_file = include_file.replace('%h', hostname)

    return include_file


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
