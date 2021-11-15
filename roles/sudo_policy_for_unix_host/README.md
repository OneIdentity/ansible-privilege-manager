# `sudo_policy_for_unix_host` Role

The `sudo_policy_for_unix_host` role creates CSV and HTML reports that list the version of Privilege Manager for sudo plugins and the sudo policies in use on all client hosts that are joined to the policy group.

## Requirements

The role requires the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) policy server to be installed and configured on all managed nodes.

The role requires [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) version 7.2.x or later.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Facts generation

Facts generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role facts generation variables](../common/README.md#facts-generation) in the [`common`](../common/README.md) role.

* `sudo_policy_for_unix_host_facts_generate` enables facts generation.  Implicitely enabled if `sudo_policy_for_unix_host_reports_generate` is set.

    Default value is:
    ```yaml
    sudo_policy_for_unix_host_facts_generate: "{{ facts_generate }}"
    ```

### Report generation

Report generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role report generation variables](../common/README.md#report-generation) in the [`common`](../common/README.md) role.

* `sudo_policy_for_unix_host_reports_generate` enables report generation.  Reports are generated at the end of a `sudo_policy_for_unix_host` run for all hosts.

    Default value is:
    ```yaml
    sudo_policy_for_unix_host_reports_generate: "{{ reports_generate }}"
    ```

* `sudo_policy_for_unix_host_reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    sudo_policy_for_unix_host_reports_backup: "{{ reports_backup }}"

    ```

* `sudo_policy_for_unix_host_reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    sudo_policy_for_unix_host_reports_host: "{{ reports_host }}"
    ```

* `sudo_policy_for_unix_host_reports` is a list of dictionaries that define the reports to be generated.  The default value creates a CSV and HTML report using the templates included with the `sudo_policy_for_unix_host` role.

  Default value is:
    ```yaml
    sudo_policy_for_unix_host_reports:
      - src:  sudo_policy_for_unix_host_report.csv.j2
        dest: sudo_policy_for_unix_host_report.csv
      - src:  sudo_policy_for_unix_host_report.html.j2
        dest: sudo_policy_for_unix_host_report.html
    ```

  The `src` key for each list entry is the report template file on the Ansible control node.  With a relative path Ansible will look in the `sudo_policy_for_unix_host` role `template` directory.  Use a absolute path to speciy templates located elsewhere on the Ansible control node.

  The `dest` key for each list entry is the report file on the machine specified in `sudo_policy_for_unix_host_reports_host`.  If `sudo_policy_for_unix_host_reports_host` is set to the Ansible control node a relative path can be used and it will be relative to the directory from which the playbook is run.  For other hosts, an absolute path must be used.  In either case the containing directory must exist.

## Plugins

The `sudo_policy_for_unix_host` role contains two plugins to support operation of the role:

* `get_sudo_policy_for_unix_host` module runs pmsrvinfo binary and returns its results.

* `latestsudopolicies` filter takes a list of policy plugins and returns a new list of policy plugins that only includes the latest plugins for each host.

## Usage

Below is a sample playbook using the `sudo_policy_for_unix_host` role.

```yaml
---

- hosts: all

  vars:

    # Facts
    sudo_policy_for_unix_host_facts_generate: true

    # Reports
    sudo_policy_for_unix_host_reports_generate: true
    sudo_policy_for_unix_host_reports_backup: false

  roles:
    - name: oneidentity.privilege_manager.sudo_policy_for_unix_host
```

For a copy of this and other sample playbooks see [examples](../../examples/README.md)
