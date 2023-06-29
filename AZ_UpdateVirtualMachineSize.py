import sys, getopt, os
import json

from azure_api import AzAsr, AzSubscription, AzResourceGroups, AzVirtualMachine

SUBSCRIPTION_NAME = 'Enterprise Dev/Test'

def main(argv):
    tenant_id = ''
    client_id = ''
    client_secret = ''
    resource_group_name = ''
    vm_list = ''
    vm_size = ''
    try:
        opts, args = getopt.getopt(argv,'t:i:s:r:v:p:',['tenant_id=','client_id=','client_secret=', 'resource_group', 'vm_list', 'vm_size'])
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
        elif opt in ('-v', '--vm_list'):
            vm_list = arg
        elif opt in ('-p', '--vm_size'):
            vm_size = arg

    az_sub = AzSubscription()
    az_auth = az_sub.get_az_token(tenant_id, client_id, client_secret)
    sub_list = az_sub.get_all_subs()
    sub_id = next(sub['id'] for sub in sub_list if sub['displayName'] == SUBSCRIPTION_NAME)

    az_virtualmachine = AzVirtualMachine(sub_id, az_auth, "2020-12-01")

    for vm_name in vm_list.replace(' ','').split(','):
        try:
            virtualMachine = az_virtualmachine.get_vm(resource_group_name, vm_name)
        except:
            print(f"Can not find virtual machine {vm_name}")
            continue
        

        if virtualMachine['properties']['hardwareProfile']['vmSize'] != vm_size:
            virtualMachine['properties']['hardwareProfile']['vmSize'] = vm_size
            try:
                update_resp = az_virtualmachine.update_vm(resource_group_name, vm_name, virtualMachine['properties'])
            except:
                print(f"Failed to update size of virtual machine {vm_name}")
                continue
            
            if update_resp['properties']['hardwareProfile']['vmSize'] == vm_size:
                print(f"Successfully update size of virtual machine {vm_name} to {vm_size}")
            else:
                print(f"Failed to update size of virtual machine {vm_name}")
                continue

#End of main

if __name__ == "__main__":
   main(sys.argv[1:])
