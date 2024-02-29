# `join` Role

The `join` role performs [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) policy server joins and unjoins.  Report generation can be enabled to provide CSV and HTML reports of the results.

## Requirements

The role requires the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) Unix agent or sudo plugin software be installed on the client and a configured policy server.  See [`software`](../software/README.md) role for how to peform software installation of the Unix agent, sudo plugin, and policy server software using Ansible.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Join

See [join variables](../common/README.md#join-settings) in the [`common`](../common/README.md) role.

* `join_state` sets the desired join state.  Possible state values:

    * `joined` joined to specified policy server.
    * `unjoined` unjoined from any policy server.

    Default value is:
    ```yaml
    join_state: joined
    ```

* `join_password` sets the password used to authenticate with the `join_server`.  Secrets do not have to be provided in plain text, see [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) for futher information.

    Default value is:
    ```yaml
    join_password: ''
    ```

### Pmjoin Binary

* `join_extra_args` allows passing additional arguments to the pmjoin binary.

    Default value is:
    ```yaml
    join_extra_args: ''
    ```

### Facts generation

Facts generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role facts generation variables](../common/README.md#facts-generation) in the [`common`](../common/README.md) role.

* `join_facts_generate` enables facts generation.  Implicitely enabled if `join_reports_generate` is set.

    Default value is:
    ```yaml
    join_facts_generate: "{{ facts_generate }}"
    ```

* `join_facts_verbose` enables verbose facts generation.

    Default value is:
    ```yaml
    join_facts_verbose: "{{ facts_verbose }}"
    ```

### Report generation

Report generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role report generation variables](../common/README.md#report-generation) in the [`common`](../common/README.md) role.

* `join_reports_generate` enables report generation.  Reports are generated at the end of a `join` run for all hosts.

    Default value is:
    ```yaml
    join_reports_generate: "{{ reports_generate }}"
    ```

  Disabling report generation if not needed will increase the speed of the `join` role.

* `join_reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    join_reports_backup: "{{ reports_backup }}"

    ```

* `join_reports_details_format` sets the format of the details section in both the HTML and CSV reports.  Valid options:
    * `yaml` details will be in YAML format
    * `json` details will be in JSON format

    Default value is:
    ```yaml
    join_reports_details_format: "{{ reports_details_format }}"

    ```

* `join_reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    join_reports_host: "{{ reports_host }}"
    ```

* `join_reports` is a list of dictionaries that define the reports to be generated.  The default value creates a CSV and HTML report using the templates included with the `join` role.

  Default value is:
    ```yaml
    join_reports:
      - src:  join_report.csv.j2
        dest: join_report.csv
      - src:  join_report.html.j2
        dest: join_report.html
    ```

  The `src` key for each list entry is the report template file on the Ansible control node.  With a relative path Ansible will look in the `join` role `template` directory.  Use a absolute path to speciy templates located elsewhere on the Ansible control node.

  The `dest` key for each list entry is the report file on the machine specified in `join_reports_host`.  If `join_reports_host` is set to the Ansible control node a relative path can be used and it will be relative to the directory from which the playbook is run.  For other hosts, an absolute path must be used.  In either case the containing directory must exist.

## Plugins

The `join` role contains a plugin to support operation of the role:

* `pmjoin` module performs policy server join/unjoin tasks on host by wrapping the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) pmjoin binary join and unjoin commands.

## Usage

Below is a sample playbook using the `join` role.

```yaml
---
- hosts: all
  gather_facts: false

  # The variables you would most likely want/need to override have been included
  vars:

    # Join
    join_server: 10.10.10.10
    join_state: joined
    join_password: pass
    join_extra_args: ''

    # Facts
    join_facts_generate: true
    join_facts_verbose: false

    # Reports
    join_reports_generate: true
    join_reports_backup: false

  roles:
    - name: oneidentity.privilege_manager.join
```

For a copy of this and other sample playbooks see [examples](../../examples/README.md)
