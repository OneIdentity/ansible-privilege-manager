**One Identity open source projects are supported through [One Identity GitHub issues](https://github.com/OneIdentity/ars-ps/issues) and the [One Identity Community](https://www.oneidentity.com/community/). This includes all scripts, plugins, SDKs, modules, code snippets or other solutions. For assistance with any One Identity GitHub project, please raise a new Issue on the [One Identity GitHub project](https://github.com/OneIdentity/ars-ps/issues) page. You may also visit the [One Identity Community](https://www.oneidentity.com/community/) to ask questions.  Requests for assistance made through official One Identity Support will be referred back to GitHub and the One Identity Community forums where those requests can benefit all users.**

# Privilege Manager Ansible Collection

The One Identity Privilege Manager Ansible Collection, referred to as `ansible-privilege-manager`, consists of roles, modules, plugins, report templates, and sample playbooks to automate software deployment, configuration, policy server joining, and report generation for [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/).

## Collection Contents

* [`common role`](roles/common/README.md): Common tasks and variables required by other roles.

* [`preflight role`](roles/preflight/README.md): Check server readiness for software install and Policy Server create.  Check client readiness for software install and Policy Server join.
    * [`preflight module`](roles/preflight/README.md#plugins) Performs preflight tasks on host.

* [`software role`](roles/software/README.md): Server and client software install, upgrade, downgrade, uninstall, and version checking.
    * [`software_pkgs module`](roles/software/README.md#plugins) Server and client software install package directory checking.
    * [`pkgdict2items filter`](roles/software/README.md#plugins) Server and client software package sorting by state and name.

* [`join role`](roles/join/README.md): Client Policy Server joining/unjoining.
    * [`pmjoin module`](roles/join/README.md#plugins) Performs Policy Server join/unjoin tasks on host.

* [`sudoers role`](roles/sudoers/README.md): Gathers sudoers file information including included sudoers files and directories.  User and group information can be gathered as well.
    * [`get_sudoers module`](roles/sudoers/README.md#plugins) Returns the list of sudoers files (the main sudoers and all other included sudoers files) and a single complete sudoers file in which all include directives have been replaced by the content of the included files.
    * [`save_sudoers module`](roles/sudoers/README.md#plugins) Saves the complete sudoers file on the controller node.

* [`sudo_policy_for_unix_host role`](roles/sudo_policy_for_unix_host/README.md): List the version of Privilege Manager for sudo plugins and the sudo policies in use on all client hosts that are joined to the policy group.
    * [`get_sudo_policy_for_unix_host module`](roles/sudo_policy_for_unix_host/README.md#plugins): Runs pmsrvinfo binary and returns its results.
    * [`latestsudopolicies filter`](roles/sudo_policy_for_unix_host/README.md#plugins) Selects the latest plugins for each host.

## Installation

### Prerequisites

* [Ansible](https://github.com/ansible/ansible) version 2.9 or later

    * `Collections are a new feature introduced in Ansible version 2.9.  Please use the latest 2.9+ release for the best user experience.`

* [Jinja](https://github.com/pallets/jinja) version 2.10 or later.

* [Privilege Manager](https://www.oneidentity.com/products/privilege-manager-for-sudo/) version 6.1.x or later

    * `This collection expects the components and structure of Privilege Manager 6.1.x or later.`
    * See collection role documentation for specific, per-role  requirements and instructions.
    * See [Privilege Manager documentation](https://support.oneidentity.com/privilege-manager-for-sudo/6.1.1/technical-documents) for requirements and instructions.

### From Ansible Galaxy

To install from [Ansible Galaxy](https://galaxy.ansible.com/) you can use the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command to install the collection on your control node.  See [Ansible documentation](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html#installing-collections) for futher information.

Using `ansible-galaxy` command:
```bash
ansible-galaxy collection install oneidentity.privilege_manager
```

The collection can also be added to a project's `requirements.yml` file
```yaml
---
collections:
  - name: oneidentity.privilege_manager
```

and installed using the `ansible-galaxy` command.  This method allows all required collections for a project to be specified in one place and installed with one command.
```bash
ansible-galaxy collection install -r requirements.yml
```

When used with [Ansible Tower](https://www.ansible.com/products/tower) and [Ansible AWX](https://github.com/ansible/awx) the collections in the project's `requirements.yml` file are automatically installed each time a project is run and there is no need to use the `ansible-galaxy` command.

### From GitHub

For the examples in this section please see `ansible-privilege-manager` [releases page](https://github.com/OneIdentity/ansible-privilege-manager/releases) to find the latest collection build artifact (*.tar.gz file) and use the URL to this file in place of the URL's shown below.  The collection build artifact is under the 'Assets' section for each release (right click on the *.tar.gz file and select 'Copy link address' to copy URL).

To install from [GitHub](https://github.com/OneIdentity/ansible-privilege-manager) you can use the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command to install the collection on your control node.  See [Ansible documentation](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html#installing-collections) for futher information.

Using `ansible-galaxy` command:
```bash
ansible-galaxy collection install https://github.com/OneIdentity/ansible-privilege-manager/releases/download/v0.1.3/oneidentity-privilege_manager-0.1.3.tar.gz
```

The collection can also be added to a project's `requirements.yml` file
```yaml
---
collections:
  - name: https://github.com/OneIdentity/ansible-privilege-manager/releases/download/v0.1.3/oneidentity-privilege_manager-0.1.3.tar.gz
```

and installed using the `ansible-galaxy` command.  This method allows all required collections for a project to be specified in one place and installed with one command.
```bash
ansible-galaxy collection install -r requirements.yml
```

When used with [Ansible Tower](https://www.ansible.com/products/tower) and [Ansible AWX](https://github.com/ansible/awx) the collections in the project's `requirements.yml` file are automatically installed each time a project is run and there is no need to use the `ansible-galaxy` command.

### Local Build and Install

For local build and installation, you can clone the Git repository, build the collection artifact, and install the locally built collection artifact.  This would be useful for those wishing to extend or customize the collection.

1. Clone the Git repository:

    ```bash
    git clone https://github.com/OneIdentity/ansible-privilege-manager.git
    ```

2. Run a local build inside the collection using the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command in the root directory of the cloned repository:

    ```bash
    cd ansible-privilege-manager
    ansible-galaxy collection build
    ```

    The build command will generate an Ansible Galaxy collection artifact with a `tar.gz` file extension, sample output will look like the following:

    ```
    Created collection for oneidentity.privilege_manager at /home/user/ansible-privilege-manager/oneidentity-privilege_manager-0.1.3.tar.gz
    ```

    `Pleae note the path shown above is just an example, the path to your build artifact will be in the root directory of the cloned repository.`

3. Install the locally-built collection artifact using the [ansible-galaxy](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html) command to install the collection on your control node.  See [Ansible documentation](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html#installing-collections) for futher information.

    Using `ansible-galaxy` command:

    ```bash
    ansible-galaxy collection install /home/user/ansible-privilege-manager/oneidentity-privilege_manager-0.1.3.tar.gz
    ```

    The collection can also be added to a project's `requirements.yml` file
    ```yaml
    ---
    collections:
    - name: /home/user/ansible-privilege-manager/oneidentity-privilege_manager-0.1.3.tar.gz
    ```

    and installed using the `ansible-galaxy` command.  This method allows all required collections for a project to be specified in one place and installed with one command.
    ```bash
    ansible-galaxy collection install -r requirements.yml
    ```

When used with [Ansible Tower](https://www.ansible.com/products/tower) and [Ansible AWX](https://github.com/ansible/awx) the collections in the project's `requirements.yml` file are automatically installed each time a project is run and there is no need to use the `ansible-galaxy` command.

## Usage

The collection provides various sample playbooks in the [examples](examples/README.md) directory.

## Supported Platforms

All [Privilege Manager supported platforms](https://support.oneidentity.com/technical-documents/privilege-manager-for-sudo/6.1.1/release-notes#TOPIC-1389219).

## Notes

### Known issues

* Check mode does not work as expected for the software role.  No changes are made and it doesn't cause errors but the stated changes that would or would not be made if run normally are not accurate.
* The directory of software install packages has to be on the Ansible control node.  It would be nice to be able to point to this directory on another machine but this is not possible at this time.
* The IPV4 address for HP-UX machines does not show up in the CSV and HTML reports, this is due to differences in how facts are reported for this OS.  No plan to fix this issue at this time.
* MacOS uninstall of Privilege Manager for Unix client.  Package does not currently have an uninstaller.  Uninstaller will be added in future release of Privilege Manager.

