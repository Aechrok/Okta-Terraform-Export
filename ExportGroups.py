from http.client import NOT_FOUND
import json, argparse
import requests

# Add commandline arguments.
def parseArguments():
    parser = argparse.ArgumentParser(description='Query all groups in Okta and output Terraform resources and import commands.', epilog='Created by https://github.com/Aechrok')

    parser.add_argument('-u', '--url', help='URL to the Okta Instance. (Example: <instance_name>.okta.com)', type=str, required=True)
    parser.add_argument('-t', '--token', help='Okta API token with permissions to view groups.', type=str, required=True)
    parser.add_argument('-f', '--filter', help='Filter the returned groups from Okta using the group name.', type=str, default='')

    args = parser.parse_args()
    return args

# Okta request
def get(url, token):
    # Strip https:// if found.
    if url.startswith('https://'):
        url = url.replace('https://', '')

    # Set the headers and payload
    headers = {
            'accept': 'application/json',
            'authorization': 'SSWS %s' % token,
            'content-type': 'application/json'
    }

    # Make request for all the groups
    r = requests.get(url='https://' + url + '/api/v1/groups',
                            headers=headers)

    return r.json()

# Main function to export all groups in a format Terraform expects. Recommended to run 'terraform fmt' to properly align brackets.
def func():

    args = parseArguments()

    okta_groups = get(args.url, args.token)

    group_count = 0

    print('---- Starting Export ----')
    for groups in okta_groups:
        # We only care about Okta-mastered groups.
        if not groups['type'] == "OKTA_GROUP":
            continue
        # Apply the filter, if any.
        if groups['profile']['name'].startswith(str(args.filter)):
            og = {}
            attr = {}

            # Set the name and description
            og['name'] = groups['profile']['name']
            og['description'] = groups['profile']['description']
            
            # Remove name and description from attributes for custom_profile_attributes
            groups['profile'].pop('name', NOT_FOUND)
            groups['profile'].pop('description', NOT_FOUND)
            # Combine all remaining attributes into a dictionary
            for k,v in groups['profile'].items():
                attr[k] = v

            # Prints the name of the group that is being imported to the console.
            print(og['name'])

            # Sanitizes the terraform group name: Can only contain letters, underscores, digits, or dashes
            tf_name = og['name'].replace('-','_')
            tf_name = tf_name.replace(' ','_')
            tf_name = tf_name.replace('/','_')
            tf_name = tf_name.replace(':','_')
            tf_name = tf_name.replace('@','_')
            tf_name = tf_name.replace(',','_')
            tf_name = tf_name.replace('(','_')
            tf_name = tf_name.replace(')','_')

            # Write The resource to the terraform file.
            with open('OktaGroups.tf', 'a') as f:
                f.write('resource "okta_group" "{}" {{\n'.format(tf_name))
                f.write('  name = "{}"\n'.format(og['name']))
                f.write('  description = "{}"\n'.format(og['description']))
                f.write('  custom_profile_attributes = jsonencode({})\n'.format(json.dumps(attr, indent=4)))
                f.write('  skip_users = true\n') # Imports groups without worrying about user assignments.
                f.write('}\n\n')

            # Write the terraform import command to a file for easy importing of existing groups.
            with open('OktaTerraformImport.sh', 'a') as f:
                f.write('terraform import okta_group.{} {}\n'.format(tf_name, groups['id']))

            group_count += 1
    print('---- Export Complete ----')
    print('Total Groups exported: {}'.format(group_count))
    print('-------------------------')

if __name__ == "__main__":
    func()
else:
    print('The script must be run directly.')
    exit(2)