#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2020, One Identity LLC
# File: vastool.py
# Desc: Shared code for pmjoin module
# Auth: Mark Stillings
# Note:
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import sys
import subprocess
import re
import ansible_collections.oneidentity.privilege_manager.plugins.module_utils.check_file_exec as cfe


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

BASE_DIR = '/opt/quest/sbin'

PMJOIN_AGENT_FILE = 'pmjoin'
PMINFO_AGENT_FILE = 'pmclientinfo'

PMJOIN_PLUGIN_FILE = 'pmjoin_plugin'
PMINFO_PLUGIN_FILE = 'pmplugininfo'

PMJOIN_AGENT_PATH = BASE_DIR + '/' + PMJOIN_AGENT_FILE
PMJOIN_PLUGIN_PATH = BASE_DIR + '/' + PMJOIN_PLUGIN_FILE

PMINFO_AGENT_PATH = BASE_DIR + '/' + PMINFO_AGENT_FILE
PMINFO_PLUGIN_PATH = BASE_DIR + '/' + PMINFO_PLUGIN_FILE


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

# TODO: Make funciton to find which binary is present if any (check_file_exec.py)

# TODO: Make function below return join status


# ------------------------------------------------------------------------------
def pmjoin_find():
    """
    Find which pmjoin binary is present to determine if this is an agent or plugin environment
    """

    err = None
    join_path = None
    info_path = None
    join_version = ''

    pmjoin_agent_cfe = cfe.check_file_exec(PMINFO_AGENT_PATH, '-v')
    pmjoin_plugin_cfe = cfe.check_file_exec(PMINFO_PLUGIN_PATH, '-v')

    if not pmjoin_agent_cfe[0]:
        join_path = PMJOIN_AGENT_PATH
        info_path = PMINFO_AGENT_PATH
        join_version = pmjoin_agent_cfe[1]

    elif not pmjoin_plugin_cfe[0]:
        join_path = PMJOIN_PLUGIN_PATH
        info_path = PMINFO_PLUGIN_PATH
        join_version = pmjoin_plugin_cfe[1]

    else:
        err = 'pmjoin not found'

    return err, join_path, info_path, join_version


# ------------------------------------------------------------------------------
def pmjoin_status():
    """
    Call pm*info to get status
    """

    # Return values
    policy_group = None

    pmpath = pmjoin_find()
    if pmpath[0]:
        return policy_group

    # Build pm*info command
    cmd = []
    cmd += [pmpath[2]]
    cmd += ['-c']

    # Call pm*info
    try:
        rval_bytes = subprocess.check_output(' '.join(cmd), stderr=subprocess.STDOUT, shell=True)
    # This exception happens when the process exits with a non-zero return code
    except subprocess.CalledProcessError as e:
        # Just grab output bytes likes a normal exit, we'll parse it for errors anyway
        rval_bytes = e.output
    # check_output returns list of bytes so we have to decode to get a string
    rval_str = rval_bytes.decode(sys.stdout.encoding)

    # Parse vastool return
    policy_group = pmjoin_status_parse(rval_str)

    # Return
    return policy_group


# ------------------------------------------------------------------------------
def pmjoin_status_parse(rval_str):

    # Return values
    policy_server = None

    # Find if joined
    joined = False
    join_re_str = r'Joined to a policy group,(\S+)$'
    join_re = re.compile(join_re_str, re.MULTILINE)
    join_re_match = join_re.split(rval_str)
    if len(join_re_match) > 1 and join_re_match[1] == 'YES':
        joined = True

    # Find server
    if joined:
        group_re_str = r'Hostname of primary policy server,(.+)$'
        group_re = re.compile(group_re_str, re.MULTILINE)
        group_re_match = group_re.split(rval_str)
        if len(group_re_match) > 1:
            policy_server = group_re_match[1]

    # Return
    return policy_server
