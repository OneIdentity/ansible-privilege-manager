#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2020, One Identity LLC
# File: software_pkgs.py
# Desc: Ansible module that checks package install directory
#       for packages for the specified system, distribution, and architecture.
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
module: software_pkgs

short_description: Checks and parses Privilege Manager software install directory

version_added: '2.9'

description: >
    Checks and parses Privilege Manager software install directory to find list
    of software packages per the provided mode (mode), system (sys),
    distribution (dist), architecture (arch), at the specified path (path)

options:
    mode:
        description:
            - Mode (server, pmpolicy, sudo, all)
        required: true
    sys:
        description:
            - System (Linux, FreeBSD, Solaris, etc.)
        required: true
    dist:
        description:
            - Distribution (Redhat, Debian, etc.)
        required: true
    arch:
        description:
            - Architecture (x86, amd64, etc.)
        required: true
    path:
        description:
            - Software directory
        required: true
    facts:
        description:
            - Generate Ansible facts?
        type: bool
        required: false
        default: false
    facts_key:
        description:
            - Ansible facts key
        type: str
        required: false
        default: 'software_pkgs'

author:
    - Mark Stillings (mark.stillings@oneidentity.com)
"""

EXAMPLES = """
- name: Normal usage
  software_pkgs:
    mode: sudo
    sys: linux
    dist: debian
    arch: amd64
    path: /var/tmp/privilege_manager/sw
  register: software_pkgs_result
"""

RETURN = """
params:
    description: Parameters passed in
    type: dict
    returned: always
packages:
    description: The discovered packages and versions in supplied path
    type: dict
    returned: always
ansible_facts:
    description: All return data is placed in Ansible facts
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
        packages:
            description: The discovered packages and versions in supplied path
            type: dict
            returned: always
"""


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
import os
import traceback
import glob
import re


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

# Arg choices and defaults
FACTS_DEFAULT = False
FACTS_KEY_DEFAULT = 'sas_software_pkgs'

# Package paths for all supported systems and architectures
PKG_PATHS = {
    'linux': {
        'i386': 'linux-intel',
        'x86_64': 'linux-x86_64',
        'amd64': 'linux-x86_64',
        'ppc64': 'linux-ppc64',
        'ppc64le': 'linux-ppc64le',
        'aarch64': 'linux-aarch64',
        'ia64': 'linux-ia64',
        's390': 'linux-s390',
        's390x': 'linux-s390x'
    },
    'freebsd': {
        'x86_64': 'freebsd-x86_64',
        'amd64': 'freebsd-x86_64'
    },
    'sunos': {
        'i386': 'solaris-intel',
        'x86_64': 'solaris-intel',
        'amd64': 'solaris-intel',
        'sparc': 'solaris-sparc',
        'sparc64': 'solaris-sparc'
    },
    'darwin': {
        'x86_64': 'macosx-x86_64'
    },
    'hp-ux': {
        '9000/800': 'hpux-hppa11',
        'ia64': 'hpux-aarch64'
    },
    'aix': {
        'chrp': 'aix71-rs6k'
    },
}

# Package file extensions for all supported distributions
PKG_EXTENSIONS = {
    'debian': 'deb',
    'ubuntu': 'deb',
    'redhat': 'rpm',
    'centos': 'rpm',
    'suse': 'rpm',
    'freebsd': 'txz',
    'solaris': 'pkg',
    'darwin': 'pkg',
    'hp-ux': 'depot',
    'aix': 'bff'
}

# Modes
MODE_CHOICES = ['all', 'server', 'pmpolicy', 'sudo']

# Package sub-directories
PKG_SUB_DIRS = {
    'server': 'server',
    'pmpolicy': 'agent',
    'sudo': 'sudo_plugin'
}

# Package keys
PKG_KEYS = {
    'server': 'server',
    'agent': 'agent',
    'sudo_plugin': 'plugin'
}


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
                'choices': MODE_CHOICES,
                'required': True
            },
            'sys': {
                'type': 'str',
                'required': True
            },
            'dist': {
                'type': 'str',
                'required': True
            },
            'arch': {
                'type': 'str',
                'required': True
            },
            'path': {
                'type': 'str',
                'required': True
            },
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
            'msg': '',
            'params': {},
            'packages': {}
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

    # Exit - success
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
    packages = {}

    # Parameters
    mode = params['mode'].lower()
    sys = params['sys'].lower()
    dist = params['dist'].lower()
    arch = params['arch'].lower()
    path = params['path']
    facts = params['facts']
    facts_key = params['facts_key'] if params['facts_key'] else FACTS_KEY_DEFAULT

    try:

        # Check directory
        err = check_dir(path)

        # Check mode
        err, sub_dirs = check_mode(mode)

        # Find packages
        if err is None:
            for sub_dir in sub_dirs:
                err, p = find_packages(path, sub_dir, sys, dist, arch)
                if err is None:
                    packages.update(p)
                else:
                    break

            if not err and not packages:
                err = 'No packages found for sys=' + sys + ', dist=' + dist + ', arch=' + arch

    except Exception:
        tb = traceback.format_exc()
        err = str(tb)

    # Build result
    result['changed'] = False   # Never makes any changes to the host
    result['failed'] = err is not None
    result['msg'] = err if err is not None else ''
    result['params'] = params
    result['packages'] = packages

    # Create ansible_facts data
    if facts:
        result_facts = result.copy()
        result['ansible_facts'] = {facts_key: result_facts}

    # Return
    return err, result


# ------------------------------------------------------------------------------
def check_dir(path):
    """
    Check if software source directory exists
    """

    # Return value
    err = None

    # Check directory
    exists = os.path.exists(path)
    isdir = os.path.isdir(path)

    # Path does not exist
    if not exists:
        err = path + ' does not exist'

    # Path is a file
    elif not isdir:
        err = path + ' is a file not a directory'

    # Return
    return err


# ------------------------------------------------------------------------------
def check_mode(mode):
    """
    Check mode and return sub directories
    """

    # Return value
    err = None
    sub_dirs = []

    # Mode is valid
    if mode in MODE_CHOICES:
        if mode == 'all':
            for m in MODE_CHOICES[1:]:
                sub_dirs += [PKG_SUB_DIRS[m]]
        else:
            sub_dirs = [PKG_SUB_DIRS[mode]]

    # Invalid mode
    else:
        err = 'mode ' + mode + ' is not a valid mode, valid modes are: ' + ', '.join(PKG_SUB_DIRS.keys())

    # Return
    return err, sub_dirs


# ------------------------------------------------------------------------------
def find_packages(sw_path, sub_dir, sys, dist, arch):
    """
    Find packages
    """

    # Return values
    err = None
    packages = {}

    # Find package path for specified sys and arch
    err, pkgs_dir = find_packages_path(sys, arch)

    # Get package extension for distribution
    if not err:
        err, pkgs_ext = find_packages_ext(dist)

    # Find packages
    if not err:
        pkgs_path = sw_path + '/' + sub_dir + '/' + pkgs_dir
        pkgs_key = PKG_KEYS[sub_dir]
        print('pkgs_path: ' + pkgs_path)
        err, packages = parse_packages(pkgs_path, pkgs_ext, pkgs_key)

    # Find preflight
    if not err:
        packages['pmpreflight'] = find_preflight(pkgs_path)

    # Return
    return err, packages


# ------------------------------------------------------------------------------
def find_packages_path(sys, arch):
    """
    Find package path for specified sys and arch
    """

    # Return values
    err = None
    path = ''

    # Find path info
    if sys in PKG_PATHS:
        sys_archs = PKG_PATHS[sys]

        if arch in sys_archs:
            path = sys_archs[arch]

        else:
            err = 'Unsupported architecture ' + arch

    else:
        err = 'Unsupported system ' + sys

    return err, path


# ------------------------------------------------------------------------------
def find_packages_ext(dist):
    """
    find package file extension for specified OS distribution
    """

    # Return values
    err = None
    ext = ''

    # Find extension info
    if dist in PKG_EXTENSIONS:
        ext = PKG_EXTENSIONS[dist]

    else:
        err = 'Unsupported distribution ' + dist

    return err, ext


# ------------------------------------------------------------------------------
def parse_packages(path, ext, pkg_key):
    """
    Parse packages
    """

    # Return values
    err = None
    packages = {}

    # regex strings
    pkg_name_re_str = r'^[a-z]+[-]*[a-z]*(?=\D)'
    pkg_vers_re_str = r'(?=.*)[\d]+\.[\d]+\.[\d]+[\.-][\d]+(?=\D)'

    # Compile regex's
    pkg_name_re = re.compile(pkg_name_re_str, re.I)
    pkg_vers_re = re.compile(pkg_vers_re_str)

    # Glob the package directory to find packages with correct file extension
    pkgs_str = path + '*/*.' + ext
    pkgs = glob.glob(pkgs_str)

    # Parse each package
    for pkg in pkgs:

        pkg_path = pkg
        pkg_file = os.path.basename(pkg_path)

        pkg_name = None
        pkg_name_match = pkg_name_re.search(pkg_file)
        if pkg_name_match:
            pkg_name = pkg_name_match.group()

        pkg_vers = ''
        pkg_vers_match = pkg_vers_re.search(pkg_file)
        if pkg_vers_match:
            pkg_vers = pkg_vers_match.group()
            pkg_vers = pkg_vers.replace('-', '.')

        if pkg_name:
            packages[pkg_key] = {
                    'name': pkg_name,
                    'path': pkg_path,
                    'file': pkg_file,
                    'vers': pkg_vers
                }

    return err, packages


# ------------------------------------------------------------------------------
def find_preflight(path):
    """
    Find preflight
    """

    # Return values
    preflight = None

    # Glob the package directory to find preflight
    pkgs_str = path + '/pmpreflight'
    pkgs = glob.glob(pkgs_str)

    # Found it
    if pkgs:
        preflight = {
                'name': 'pmpreflight',
                'path': pkgs[0],
                'file': 'pmpreflight',
                'vers': ''
            }

    # Nope
    else:
        preflight = {
                'name': 'pmpreflight',
                'path': '',
                'file': 'pmpreflight',
                'vers': ''
            }

    return preflight


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
