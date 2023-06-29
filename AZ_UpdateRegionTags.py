#the below python script to update tag values in the azure services.

import sys, getopt, os
from datetime import datetime
import pandas as pd

from azure_api import AzAsr, AzSubscription, AzResourceGroups, AzTags
from libs import GenerateReport

SUBSCRIPTION_NAME = 'Enterprise Dev/Test'

def main(argv):
    tenant_id = ''
    client_id = ''
    client_secret = ''
    resource_group_name = ''
    tag = ""
    try:
        opts, args = getopt.getopt(argv,'t:i:s:r:g:o:',['tenant_id=','client_id=','client_secret=', 'resource_group', 'tag', 'operation'])
    except getopt.GetoptError:
        print(f'ERROR: {os.path.basename(__file__)} with incorrect arguments')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-t', '--tenant_id'):
            tenant_id = arg
        elif opt in ('-i', '--client_id'):
            client_id = arg
        elif opt in ('-s', '--client_secret'):
            client_secret = arg
        elif opt in ('-r', '--resource_group'):
            resource_group_name = arg
        elif opt in ('-g', '--tag'):
            tag = arg.upper()
        elif opt in ('-o', '--operation'):
            operation = arg

    tagName = tag.split(':', 1)[0]
    tagValue = tag.split(':', 1)[1]

    az_sub = AzSubscription()
    az_auth = az_sub.get_az_token(tenant_id, client_id, client_secret)
    sub_list = az_sub.get_all_subs()
    sub_id = next(sub['id'] for sub in sub_list if sub['displayName'] == SUBSCRIPTION_NAME)

    az_resourcegroup = AzResourceGroups(sub_id, az_auth)
    resource_group = az_resourcegroup.get_resourceGroup(resource_group_name)
    az_tags = AzTags(sub_id, az_auth)
    if resource_group['name'].upper() == resource_group_name.upper():
        if operation.upper() != "ENQUIRY":
            tagging = az_tags.update_tag(resource_group['id'], tagName, tagValue, operation)
            if 'successful' in tagging:
                print(f"successfully {operation} tag {tagName} with value {tagValue} for resource group {resource_group['name']}")
                vm_list = az_resourcegroup.list_instances_by_type('virtualmachine', resource_group['name'])
                for vm in vm_list:
                    try:
                        tagging = az_tags.update_tag(vm['id'], tagName, tagValue, operation)
                    except:
                        print(f"Failed to {operation} tag for vm {vm['name']}")
                    finally:
                        if 'successful' not in tagging:
                            print(f"Failed to {operation} tag for vm {vm['name']}")
                        else:
                            print(f"Successfully {operation} tag {tagName} with value {tagValue} for vm {vm['name']}")

                disk_list = az_resourcegroup.list_instances_by_type('disk', resource_group['name'])
                for disk in disk_list:
                    try:
                        tagging = az_tags.update_tag(disk['id'], tagName, tagValue, operation)
                    except:
                        print(f"Failed to {operation} tag for disk {disk['name']}")
                    finally:
                        if 'successful' not in tagging:
                            print(f"Failed to {operation} tag for disk {disk['name']}")
                        else:
                            print(f"Successfully {operation} tag {tagName} with value {tagValue} for disk {disk['name']}")
            else:
                print(f"Failed to {operation} tag for instances in Resource Group {resource_group['name']}")
                sys.exit(2)
    else:
        print(f"Failed to find Resource Group {resource_group_name}")
        sys.exit(2)

    region_tags = az_tags.get_tags(resource_group['id'])
    df = pd.json_normalize(region_tags)
    report_gen = GenerateReport()
    report_gen.create_generic_report(report_file=f"AzureReport_Tags_{resource_group['name']}.html", report_title="Tags", data=df)

#End of main

if __name__ == "__main__":
   main(sys.argv[1:])
