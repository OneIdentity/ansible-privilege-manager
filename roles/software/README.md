# `software` Role

The `software` role manages the deployment of [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) software.  The role supports software install, upgrade, downgrade, uninstall, and version checking.  Report generation can be enabled to provide CSV and HTML reports of the software state before, changes made, and state after the role is run.

## Requirements

The role requires the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) software install packages be available on Ansible control node.  See [variables](#variables) section for more detail.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Software Directories

See [software directories variables](../common/README.md#software-directories) in the [`common`](../common/README.md) role.

### Software state

* `software_pkg_state` is a dictionary containing the software packages and their state for your environment.  Possible state values:

    * `check` checks install state and reads version, no changes to the system
    * `present` ensures package is installed and the same version as the install package in `software_dir`
    * `absent` ensures package is not installed

    Default value is:

    ```yaml
    software_pkg_state:
      server: check
      agent: check
      plugin: check
    ```

    The default value for `software_pkg_state` contains all [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) packages with a state of `check` which will not make any changes to your hosts.  You'll need to override this variable to perform install, upgrade, downgrade, and uninstall of software packages.

    For example, if you wanted to make sure the sudo plugin is installed and up to date in your environment `software_pkg_state` would be set as follows:

    ```yaml
    software_pkg_state:
      plugin: present
    ```

### Facts generation

Facts generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role facts generation variables](../common/README.md#facts-generation) in the [`common`](../common/README.md) role.

* `software_facts_generate` enables facts generation.  Implicitely enabled if `software_reports_generate` is set.

    Default value is:
    ```yaml
    software_facts_generate: "{{ facts_generate }}"
    ```

* `software_facts_verbose` enables verbose facts generation.

    Default value is:
    ```yaml
    software_facts_verbose: "{{ facts_verbose }}"
    ```

### Report generation

Report generation variable defaults for all roles are set by variables in the [`common`](../common/README.md) role and can be overriden for all roles by setting the appropriate [`common`](../common/README.md) role variable.  See [common role report generation variables](../common/README.md#report-generation) in the [`common`](../common/README.md) role.

* `software_reports_generate` enables report generation.  Reports are generated at the end of a `software` run for all hosts.

    Default value is:
    ```yaml
    software_reports_generate: "{{ reports_generate }}"
    ```

  Disabling report generation if not needed will increase the speed of the `software` role.

* `software_reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    software_reports_backup: "{{ reports_backup }}"

    ```

* `software_reports_details_format` sets the format of the details section in both the HTML and CSV reports.  Valid options:
    * `yaml` details will be in YAML format
    * `json` details will be in JSON format

    Default value is:
    ```yaml
    software_reports_details_format: "{{ reports_details_format }}"

    ```

* `software_reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    software_reports_host: "{{ reports_host }}"
    ```

* `software_reports` is a list of dictionaries that define the reports to be generated.  The default value creates a CSV and HTML report using the templates included with the `software` role.

  Default value is:
    ```yaml
    software_reports:
      - src:  software_report.csv.j2
        dest: software_report.csv
      - src:  software_report.html.j2
        dest: software_report.html
    ```

  The `src` key for each list entry is the report template file on the Ansible control node.  With a relative path Ansible will look in the `software` role `template` directory.  Use a absolute path to speciy templates located elsewhere on the Ansible control node.

  The `dest` key for each list entry is the report file on the machine specified in `software_reports_host`.  If `software_reports_host` is set to the Ansible control node a relative path can be used and it will be relative to the directory from which the playbook is run.  For other hosts, an absolute path must be used.  In either case the containing directory must exist.

## Plugins

The `software` role contains a few plugins to support operation of the role:

* `software_pkgs` module checks and parses the subdirectories in the directory specified in `software_dir` to find the correct packages for each host per its OS distribution and hardware architecture.

* `pkgdict2items` filter performs software package sorting by state and name, and formats the result in the format expected by Ansible for use in looping.

## Usage

Below is a sample playbook using the `software` role that will install, upgrade, or downgrade the `plugin` package for all hosts so that after the playbook run they will the same versions as the packages found in `software_dir`.

Only the `software_dir` and `software_pkg_state` variables are overriden in this playbook so the default values will be used for all other variables.

```yaml
---

- hosts: all

  vars:

    # Directories
    software_dir: "./files/6.1.1.0"

    # Software
    software_pkg_state:
      plugin: present

    # Facts
    software_facts_generate: true
    software_facts_verbose: false

    # Reports
    software_reports_generate: true
    software_reports_backup: false

  roles:
    - name: oneidentity.privilege_manager.software
```

For a copy of this and other sample playbooks see [examples](../../examples/README.md)
