#!/usr/bin/python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# Copyright (c) 2021, One Identity LLC
# File: sudo_policy_for_unix_host_filters.py
# Desc: Ansible filters for sudo_policy_for_unix_host role
# Auth: Laszlo Nagy
# Note:
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# Future module imports for consistency across Python versions
from __future__ import absolute_import, division, print_function

# Want classes to be new type for consistency across Python versions
__metaclass__ = type

from ansible.errors import AnsibleFilterError


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
def get_latest_sudo_policies(sudo_policies_list):
    """
    Example of sudo_policies_list:
    [
        ['qpm-rhel6-64a', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37a', '1634124307'],
        ['qpm-rhel6-64b', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37b', '1634124308'],
        ['qpm-rhel6-64c', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37c', '1634124309'],
        ['qpm-rhel6-64d', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37d', '1634124310'],
        ['qpm-rhel6-64c', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37c', '1634124369'],
        ['qpm-rhel6-64d', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37d', '1634124370'],
        ['qpm-rhel6-64e', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37e', '1634124371'],
        ['qpm-rhel6-64f', '/etc/opt/quest/qpm4u/policy/sudoers', '7.1.99.7-55-g787b0a37f', '1634124372']
    ]
    """

    latest_sudo_policies = {}
    for sudo_policy in sudo_policies_list:
        hostname = sudo_policy[0]
        if hostname not in latest_sudo_policies:
            latest_sudo_policies[hostname] = sudo_policy
        else:
            if int(latest_sudo_policies[hostname][3]) < int(sudo_policy[3]):
                latest_sudo_policies[hostname] = sudo_policy

    latest_sudo_policies = list(latest_sudo_policies.values())

    return latest_sudo_policies


# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
class FilterModule(object):
    """
    sudo_policy_for_unix_host role jinja2 filters
    """

    def filters(self):
        filters = {
            'latestsudopolicies': get_latest_sudo_policies,
        }
        return filters
