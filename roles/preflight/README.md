# `preflight` Role

The `preflight` role checks client readiness for [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) software installation, policy server creation, and policy server joining.  Report generation can be enabled to provide CSV and HTML reports of the results.

## Requirements

The role requires the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) software install packages be available on Ansible control node.  See [variables](#variables) section for more detail.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Software Directories

See [software directory variables](../common/README.md#software-directories) in the[`common`](../common/README.md) role.

### Join Settings

See [join settings variables](../common/README.md#join-settings) in the [`common`](../common/README.md) role.

### Preflight Binary

* `preflight_mode` configures how preflight runs.  Possible values:

    * `sudo` checks readiness of host to install sudo plugin and join the policy server specified by the `join_server` variable.
    * `pmpolicy` checks readiness of host to install Unix agent and join the policy server specified by the `join_server` variable.
    * `server` checks readiness of host to install policy server software and to function as a policy server.

    Default value is:
    ```yaml
    preflight_mode: sudo
    ```

* `preflight_verbose` enables verbose output in all preflight modes.

    Default value is:
    ```yaml
    preflight_verbose: false
    ```

* `preflight_extra_args` allows passing additional arguments to the preflight binary.

    Default value is:
    ```yaml
    preflight_extra_args: ''
    ```

### Facts generation

Facts generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role facts generation variables](../common/README.md#facts-generation) in the [`common`](../common/README.md) role.

* `preflight_facts_generate` enables facts generation.  Implicitely enabled if `preflight_reports_generate` is set.

    Default value is:
    ```yaml
    preflight_facts_generate: "{{ facts_generate }}"
    ```

* `preflight_facts_verbose` enables verbose facts generation.

    Default value is:
    ```yaml
    preflight_facts_verbose: "{{ facts_verbose }}"
    ```

### Report generation

Report generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role report generation variables](../common/README.md#report-generation) in the [`common`](../common/README.md) role.

* `preflight_reports_generate` enables report generation.  Reports are generated at the end of a `preflight` run for all hosts.

    Default value is:
    ```yaml
    preflight_reports_generate: "{{ reports_generate }}"
    ```

  Disabling report generation if not needed will increase the speed of the `preflight` role.

* `preflight_reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    preflight_reports_backup: "{{ reports_backup }}"

    ```

* `preflight_reports_details_format` sets the format of the details section in both the HTML and CSV reports.  Valid options:
    * `yaml` details will be in YAML format
    * `json` details will be in JSON format

    Default value is:
    ```yaml
    preflight_reports_details_format: "{{ reports_details_format }}"

    ```

* `preflight_reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    preflight_reports_host: "{{ reports_host }}"
    ```

* `preflight_reports` is a list of dictionaries that define the reports to be generated.  The default value creates a CSV and HTML report using the templates included with the `preflight` role.

  Default value is:
    ```yaml
    preflight_reports:
      - src:  preflight_report.csv.j2
        dest: preflight_report.csv
      - src:  preflight_report.html.j2
        dest: preflight_report.html
    ```

  The `src` key for each list entry is the report template file on the Ansible control node.  With a relative path Ansible will look in the `preflight` role `template` directory.  Use a absolute path to speciy templates located elsewhere on the Ansible control node.

  The `dest` key for each list entry is the report file on the machine specified in `preflight_reports_host`.  If `preflight_reports_host` is set to the Ansible control node a relative path can be used and it will be relative to the directory from which the playbook is run.  For other hosts, an absolute path must be used.  In either case the containing directory must exist.

## Plugins

The `preflight` role contains a plugin to support operation of the role:

* `preflight` module performs preflight tasks on host by wrapping the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) pmpreflight binary.

## Usage

Below is a sample playbook using the `preflight` role.

```yaml
---

- hosts: all
  gather_facts: false

  # The variables you would most likely want/need to override have been included
  vars:

    # Join
    join_server: 10.10.10.10

    # Preflight
    preflight_mode: sudo
    preflight_verbose: false
    preflight_extra_args: ''

    # Directories
    software_dir: "./files/6.1.1.0"
    software_tmp_dir: /tmp/1id

    # Facts
    preflight_facts_generate: true
    preflight_facts_verbose: false

    # Reports
    preflight_reports_generate: true
    preflight_reports_backup: false

  roles:
    - name: oneidentity.privilege_manager.preflight
```

For a copy of this and other sample playbooks see [examples](../../examples/README.md)
