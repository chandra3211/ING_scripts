#!/usr/bin/scl enable rh-python36 -- python3
 
import sys
import json
import os
import errno
from jinja2 import Environment, FileSystemLoader
import shutil
from pathlib import Path
import re
from datetime import date

region_name = sys.argv[1]
region_subnet = sys.argv[2]
instance_type = sys.argv[3]
snapshot_version = sys.argv[4]
profile_json = sys.argv[5]
vm_ipv4 = sys.argv[6]
inventory_path = sys.argv[7]
hub_network = sys.argv[8]

ING_SUBNETS = ['10.51.0.0/16',
                '10.52.0.0/16',
                '10.53.0.0/16',
                '192.168.0.0/16',
                '172.21.0.0/16',	
                '172.26.0.0/23',
                '172.20.0.0/16',
                '10.54.0.0/16',
                '10.55.0.0/16',
                '10.56.0.0/16']

cwd = os.path.dirname(os.path.realpath(__file__))
templates_folder = os.path.join(cwd, 'templates/')
region_folder = os.path.join(cwd, region_name)
today = date.today()

class Nsg_rule:
    def __init__(self, direction, name, source, destination, priority):
        self.direction = direction
        self.name = name
        self.source = source
        self.destination = destination
        self.priority = priority
#end of Nsg_rule

class Hub:
    def __init__(self, rg_name, vnet, subnet):
        self.rg_name = rg_name
        self.vnet = vnet
        self.subnet = subnet

    def getvnet(self):
        return self.vnet

    def getname(self):
        return self.rg_name

    def getsubnet(self):
        return self.subnet
#end of Hub

def silentremove_folder(path):
    if os.path.exists(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        shutil.rmtree(path)
#end of silentremove_folder

def silentremove_file(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred
#end of silentremove_file

def create_region_folder(folder):
    if os.path.exists(folder):
        print(folder + ' : exists')
        if os.path.isdir(folder):
            print(folder + ' : is a directory')
    else:
        os.mkdir(folder)
#end of create_region_folder

def generate_tf_file(contents, file_name):
    new_file= open(file_name,"w+")

    new_file.write(contents)

    new_file.close()
#end of generate_tf_file

def generate_nsg_rules(subnets, in_or_out):
    rules_list = []

    for subnet in subnets:
        priority = subnets.index(subnet) + 101
        if in_or_out == 'in':
            bound_dict = 'Inbound'
            name = 'biab_from_{0}'.format(subnet.split('/')[0].replace('.', '_'))
            source = subnet
            destination = '0.0.0.0/0'
        else:
            bound_dict = 'Outbound'
            name = 'biab_to_{0}'.format(subnet.split('/')[0].replace('.', '_'))
            source = '0.0.0.0/0'
            destination = subnet

        new_rule = Nsg_rule(bound_dict, name, source, destination, priority)
        rules_list.append(new_rule)   

    return rules_list
#end of generate_nsg_rules

def create_resourcegroup():
    nsg_inbound_rules = generate_nsg_rules(ING_SUBNETS, 'in')
    nsg_outbond_rules = generate_nsg_rules(ING_SUBNETS, 'out')

    silentremove_folder(region_folder)
    create_region_folder(region_folder)

    env = Environment(loader=FileSystemLoader(templates_folder))

    backend_template = env.get_template('backend.tpl')
    backend_output = backend_template.render(region_name=region_name)
    backend_tfname = os.path.join(region_folder, "backend.tf")
    generate_tf_file(backend_output, backend_tfname)

    provider_template = env.get_template('provider.tpl')
    provider_output = provider_template.render(provider='=2.9.0')
    provider_tfname = os.path.join(region_folder, "provider.tf")
    generate_tf_file(provider_output, provider_tfname)

    #region_vn = "vn_%s_%s" % (region_subnet.split('/')[0].split('.')[2], region_subnet.split('/')[0].split('.')[3])
    region_sn = "10_53_%s_%s" % (region_subnet.split('/')[0].split('.')[2], region_subnet.split('/')[0].split('.')[3])
    mgmt_hub = Hub('biab_static_networks', hub_network, region_sn)
    variables_template = env.get_template('variables.tpl')
    variables_output = variables_template.render(hub=mgmt_hub, region_name=region_name, creation_date=today, SNAPSHOT_DATE=snapshot_version)
    variables_tfname = os.path.join(region_folder, "variables.tf")
    generate_tf_file(variables_output, variables_tfname)

    region_template = env.get_template('region.tpl')
    region_output = region_template.render(region_subnet=region_subnet, nsg_outbond_rules=nsg_outbond_rules, nsg_inbound_rules=nsg_inbound_rules, hub=mgmt_hub)
    region_tfname = os.path.join(region_folder, "region.tf")
    generate_tf_file(region_output, region_tfname)
#end of create_resourcegroup

def create_vms(vm_list):

    env = Environment(loader=FileSystemLoader(templates_folder))

    vm_template = env.get_template('vm.tpl')
    vm_output = vm_template.render(vm_list=vm_list, SNAPSHOT_DATE=snapshot_version)
    vm_tfname = os.path.join(region_folder, "vm.tf")
    generate_tf_file(vm_output, vm_tfname)
#end of create_vms

def create_vm(vm_to_add):
    
    env = Environment(loader=FileSystemLoader(templates_folder))

    vm_template = env.get_template('vm.tpl')
    vm_output = vm_template.render(vm_list=[vm_to_add], SNAPSHOT_DATE=snapshot_version)
    vm_tfname = os.path.join(region_folder, ("%s.tf" % vm_to_add.machinename))
    generate_tf_file(vm_output, vm_tfname)
#end of create_vm

def build_vm_profiles(profile_json):
    class virtual_machine:
        def __init__(self, machinename, vm_size, ostype, osdisk, data_disks, ipv4, license_type):
            self.machinename = machinename
            self.vm_size = vm_size
            self.ostype = ostype
            self.osdisk = osdisk
            self.data_disks = data_disks
            self.ipv4 = ipv4
            self.license_type = license_type

        def toJSON(self):
            obj_json = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, separators=(',', ':'))
            return json.loads(obj_json)

        def get_ipv4(self):
            return self.ipv4

        def get_datadisks(self):
            return self.data_disks

        def get_machinename(self):
            return self.machinename

        def get_vmsize(self):
            return self.vm_size

        def get_ostype(self):
            return self.ostype

        def get_osdisk(self):
            return self.osdisk

        def get_licensetype(self):
            return self.license_type
        
        def get(self):
            return self
    #end of virtual_machine:

    cwd = Path(os.path.dirname(os.path.realpath(__file__))).parent
    profile_json = 'templates/%s' % profile_json
    vm_profiles = os.path.join(cwd, profile_json)

    vm_profile_list = []
    lambda_ipaddr = lambda subnet, func: subnet[:3] + [func(subnet[-1])]
    
    with open(vm_profiles) as vm_json:
        vms = json.load(vm_json)
        for vm in vms:
            vm_data_disks = []
            for disk in vm['snapshots']:
                p = re.compile('\w*_OS$', re.IGNORECASE)
                op = p.search(disk['name'])
                if op:
                    vm_os_disk = disk['name']
                else:
                    vm_data_disks.append(disk['name'])
            vm_ipv4 = '.'.join(lambda_ipaddr(region_subnet.split('/')[0].split('.'), lambda x: str(int(x) + vms.index(vm) + 5)))
            if vm['os_type'] == 'Windows':
                vm_profile = virtual_machine(vm['name'], vm['vm_size'], vm['os_type'], vm_os_disk, vm_data_disks, vm_ipv4, 'license_type = "Windows_Server"')
            else:
                vm_profile = virtual_machine(vm['name'], vm['vm_size'], vm['os_type'], vm_os_disk, vm_data_disks, vm_ipv4, '')
            vm_profile_list.append(vm_profile)
    
    return vm_profile_list
#end of build_vm_profiles

def main():
    
    if instance_type in ['REGION', 'ALL']:
        create_resourcegroup()
    if instance_type in ['VMS', 'ALL']:
        onlyfiles = [f for f in os.listdir(inventory_path) if f.endswith('.json') and os.path.isfile(os.path.join(inventory_path, f))]
        servers = []
        for index, js in enumerate(onlyfiles):
            with open(os.path.join(inventory_path, js)) as json_file:
                json_text = json.load(json_file)
                servers.append(json_text)

        inventory_obj = []
        for dict_obj in servers:
            _computer_attr = None
            for key, value in dict_obj.items():
                if 'hosts' in value:
                    try:
                        _computer_attr
                    except NameError:
                        _computer_attr = None
                    _servers = value['hosts']
                    for _key, _value in _servers.items():
                        inventory_obj.append(_key)
        inventory_obj       

        vms_to_create = [] 
        for vm_profile in build_vm_profiles(profile_json):
            if vm_profile.machinename in inventory_obj:
                vms_to_create.append(vm_profile)
        vm_json = {'virtual_machines': []}
        for vm_to_create in vms_to_create:
            vm_json['virtual_machines'].append(vm_to_create.toJSON())

        azure_json = os.path.join(region_folder, 'azure_vm.json')
        silentremove_file(azure_json)
        with open(azure_json, 'w') as json_file:
            json.dump(vm_json, json_file)
        create_vms(vms_to_create)
    elif instance_type.upper().startswith('BIAB'):
        vm_to_create = ""
        search_by_name = lambda x, y: x.machinename == y
        for vm in build_vm_profiles(profile_json):
            if search_by_name(vm, instance_type):
                vm_to_create = vm
                break
        
        if vm_to_create == "":
            raise Exception("Can not find %s" % instance_type)

        vm_json = {'virtual_machines': []}
        vm_to_create.ipv4 = vm_ipv4
        vm_json['virtual_machines'].append(vm_to_create.toJSON())
        create_region_folder(region_folder)
        azure_json = os.path.join(region_folder, ('%s.json' % instance_type))
        silentremove_file(azure_json)
        with open(azure_json, 'w') as json_file:
            json.dump(vm_json, json_file)
        create_vm(vm_to_create)

#end of main

if __name__ == "__main__":
    main()
