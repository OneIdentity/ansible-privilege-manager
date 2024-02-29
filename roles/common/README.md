# `common` Role

The `common` role contains common tasks and variables required by other roles and is automatically included in all other roles.

## Variables

All of the variables shown below have a default value but can be overridden to suit your environment.  Variable overriding can be done in playbooks, inventories, from the command line using the `-e` switch with the `ansible-playbook` command, or from Ansible Tower and AWX.  See [Ansbile documentation](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) for further information.

### Software Directories

* `software_dir` should be set to the location of the [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) install package directory.  The subdirectories of this directory contain install packages for the server, plugin for sudo, and Unix agent for all supported systems and architectures.

    Default value is:
    ```yaml
    client_sw_dir: /tmp/1id/qpm
    ```

    For example, the install package directory for [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) 6.1.1.0 contains the following subdirectories:

    ```
    agent
    server
    sudo_plugin
    ```

* `software_tmp_dir` sets the temporary directory on Ansible hosts for storing files that need to be copied over to the hosts during software deployment operations.  The directory is created if it doesn't exist.

    Default value is:
    ```yaml
    software_tmp_dir: /tmp/1id
    ```

### Join Settings

* `join_server` sets policy server used for preflight and joining.

    Default value is:
    ```yaml
    join_server: ''
    ```

### Facts generation

Facts generation variable defaults for all roles are set by the variables below.

* `facts_generate` enables facts generation.  Implicitely enabled if `reports_generate` is set.

    Default value is:
    ```yaml
    facts_generate: true
    ```

* `facts_verbose` enables verbose facts generation.

    Default value is:
    ```yaml
    facts_verbose: true
    ```

### Report generation

Report generation variable defaults for all roles are set by the variables below.

* `reports_generate` enables report generation.

    Default value is:
    ```yaml
    reports_generate: true
    ```

  Disabling report generation if not needed will increase the speed of all roles.

* `reports_backup` enables backup of prior reports by renaming them with the date and time they were generated so that the latest reports do not override the previous reports.

    Default value is:
    ```yaml
    reports_backup: false

    ```

* `reports_details_format` sets the format of the details section in both the HTML and CSV reports.  Valid options:
    * `yaml` details will be in YAML format
    * `json` details will be in JSON format

    Default value is:
    ```yaml
    reports_details_format: yaml

    ```

* `reports_host` sets the host on which the reports should be generated.

    Default value is:
    ```yaml
    reports_host: '127.0.0.1'
    ```
