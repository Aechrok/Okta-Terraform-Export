# Okta to Terraform Group Export

Do you want to move Okta administration to Terraform, but have hundreds of existing groups in your environment? Not a problem!

### Dependencies and Requirements
Requests - [https://pypi.org/project/requests/](https://pypi.org/project/requests/)

A valid Okta instance and an Okta API key with group view permissions is required.

### Usage
```
usage: ExportGroups.py [-h] -u URL -t TOKEN [-f FILTER]

Query all groups in Okta and output Terraform resources and import commands.

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL to the Okta Instance. (Example: <instance_name>.okta.com)
  -t TOKEN, --token TOKEN
                        Okta API token with permissions to view groups.
  -f FILTER, --filter FILTER
                        Filter the returned groups from Okta using the group name.
```