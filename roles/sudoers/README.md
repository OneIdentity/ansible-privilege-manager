# `sudoers` Role

The `sudoers` role gathers sudoers file information including included sudoers files and directories.  User and groups infomration can be gathered as well.  The purpose is to view sudoers settings, users, and groups across hosts in preparation for creating a common sudoers file served from a [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) Policy Server.  Report generation can be enabled to provide CSV and HTML reports of the results.

## Requirements

None besides Ansible.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Sudoers settings

* `sudoers_tmp_dir` configures the directory on the Ansible controller to which the sudoers, users, and groups file are copied.  These files are stored in a per-host, top-level directory.

* `sudoers_passwd_mode` configures how the `passwd` file is gathered.  Possible values:

    * `skip` does not gather this file.
    * `file` gathers this file into `sudoers_tmp_dir`.

    Default value is:
    ```yaml
    sudoers_passwd_mode: skip
    ```

* `sudoers_group_mode` configures how the `group` file is gathered.  Possible values:

    * `skip` does not gather this file.
    * `file` gathers this file into `sudoers_tmp_dir`.

    Default value is:
    ```yaml
    sudoers_group_mode: skip
    ```

* `sudoers_sudoers_mode` configures how the `sudoers` file is gathered.  Possible values:

    * `skip` does not gather this file.
    * `file` gathers this file into `sudoers_tmp_dir`.

    Default value is:
    ```yaml
    sudoers_sudoers_mode: skip
    ```

* `sudoers_sudoers_includes_mode` configures how included files in the `sudoers` file are gathered.  Possible values:

    * `skip` does not gather this file.
    * `inline` gathers this file and inserts it into the main `sudoers` file.
    * `file` gathers this file into `sudoers_tmp_dir`.

    Default value is:
    ```yaml
    sudoers_sudoers_includes_mode: skip
    ```

* `sudoers_sudoers_includedirs_mode` configures how included directories in the `sudoers` file are gathered.  Possible values:

    * `skip` does not gather this directory.
    * `inline` gathers this direcory and inserts it into the main `sudoers` file.
    * `file` gathers this directory into `sudoers_tmp_dir`.

    Default value is:
    ```yaml
    sudoers_sudoers_includedirs_mode: skip
    ```

### Facts generation

Facts generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role facts generation variables](../common/README.md#facts-generation) in the [`common`](../common/README.md) role.

* `sudoers_facts_generate` enables facts generation.  Implicitely enabled if `sudoers_reports_generate` is set.

    Default value is:
    ```yaml
    sudoers_facts_generate: "{{ facts_generate }}"
    ```

* `sudoers_facts_verbose` enables verbose facts generation.

    Default value is:
    ```yaml
    sudoers_facts_verbose: "{{ facts_verbose }}"
    ```

### Report generation

Report generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role report generation variables](../common/README.md#report-generation) in the [`common`](../common/README.md) role.

* `sudoers_reports_generate` enables report generation.  Reports are generated at the end of a `sudoers` run for all hosts.

    Default value is:
    ```yaml
    sudoers_reports_generate: "{{ reports_generate }}"
    ```

  Disabling report generation if not needed will increase the speed of the `sudoers` role.

* `sudoers_reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    sudoers_reports_backup: "{{ reports_backup }}"

    ```

* `sudoers_reports_details_format` sets the format of the details section in both the HTML and CSV reports.  Valid options:
    * `yaml` details will be in YAML format
    * `json` details will be in JSON format

    Default value is:
    ```yaml
    sudoers_reports_details_format: "{{ reports_details_format }}"

    ```

* `sudoers_reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    sudoers_reports_host: "{{ reports_host }}"
    ```

* `sudoers_reports` is a list of dictionaries that define the reports to be generated.  The default value creates a CSV and HTML report using the templates included with the `sudoers` role.

  Default value is:
    ```yaml
    sudoers_reports:
      - src:  sudoers_report.csv.j2
        dest: sudoers_report.csv
      - src:  sudoers_report.html.j2
        dest: sudoers_report.html
    ```

  The `src` key for each list entry is the report template file on the Ansible control node.  With a relative path Ansible will look in the `sudoers` role `template` directory.  Use a absolute path to speciy templates located elsewhere on the Ansible control node.

  The `dest` key for each list entry is the report file on the machine specified in `sudoers_reports_host`.  If `sudoers_reports_host` is set to the Ansible control node a relative path can be used and it will be relative to the directory from which the playbook is run.  For other hosts, an absolute path must be used.  In either case the containing directory must exist.

## Plugins

None.
# Usage

Below is a sample playbook using the `sudoers` role.

```yaml
---

- hosts: all
  gather_facts: false

  # The variables you would most likely want/need to override have been included
  vars:

    # Sudoers
    sudoers_tmp_dir: /tmp/1id_sudoers
    sudoers_passwd_mode: file
    sudoers_group_mode: file
    sudoers_sudoers_mode: file
    sudoers_sudoers_includes_mode: file
    sudoers_sudoers_includedirs_mode: file

    # Facts
    sudoers_facts_generate: true
    sudoers_facts_verbose: false

    # Reports
    sudoers_reports_generate: true
    sudoers_reports_backup: false

  roles:
    - name: oneidentity.privilege_manager.sudoers
```

For a copy of this and other sample playbooks see [examples](../../examples/README.md)
