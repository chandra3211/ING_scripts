{% for vm in vm_list -%}
    resource "azurerm_network_interface" "{{vm.machinename}}_nic" {
        name                = "{{vm.machinename}}_nic"
        location            = azurerm_resource_group.rg.location
        resource_group_name = azurerm_resource_group.rg.name
        dns_servers         = ["10.54.165.65"]

        ip_configuration {
            name                          = "{{vm.machinename}}_ipconfig"
            subnet_id                     = azurerm_subnet.region_subnet.id
            private_ip_address            = "{{vm.ipv4}}"
            private_ip_address_allocation = "static"
            primary                       = "true"
        }
    }
    
    resource "azurerm_virtual_machine" "{{vm.machinename}}" {
        name                          = "${var.REGION_NAME}-{{vm.machinename}}"
        location                      = azurerm_resource_group.rg.location
        resource_group_name           = azurerm_resource_group.rg.name
        vm_size                       = "{{vm.vm_size}}"
        network_interface_ids         = [
            azurerm_network_interface.{{vm.machinename}}_nic.id
            ]
        delete_os_disk_on_termination = true

        storage_os_disk {
            name            = "{{vm.osdisk}}"
            create_option   = "Attach"
            managed_disk_id = azurerm_managed_disk.{{vm.osdisk}}.id
            os_type         = "{{vm.ostype}}"
        }

        {% for vm_datadisk in vm.data_disks -%}
        storage_data_disk {
            name             = "{{vm_datadisk}}"
            create_option    = "Attach"
            managed_disk_id  = azurerm_managed_disk.{{vm_datadisk}}.id
            lun              = "{{loop.index0}}"
            caching          = "None"
            disk_size_gb     = azurerm_managed_disk.{{vm_datadisk}}.disk_size_gb
        }
        {% endfor %}
    
        boot_diagnostics {
            enabled     = "true"
            storage_uri = format("https://%s.blob.core.windows.net", var.boot_storageaccount)
        }

        tags = {
            SNAPSHOT_DATE = var.SNAPSHOT_DATE
            CREATION_DATE = var.CREATION_DATE
            REGION_OWNER_EMAIL = var.REGION_OWNER_EMAIL
            REGION_OWNER    = var.REGION_TRIBE
            REGION_USAGE = var.REGION_USAGE_HOURS
            REGION_CREATED_BY  = var.REGION_CREATED_BY
            REGION_SUBNET  = var.REGION_SUBNET
            CATEGORY           = var.CATEGORY
            PROJECT = var.PROJECT
        }

        {{vm.license_type}}
    }

    resource "azurerm_managed_disk" "{{vm.osdisk}}" {
        name                  = "{{vm.osdisk}}"
        location              = azurerm_resource_group.rg.location
        resource_group_name   = azurerm_resource_group.rg.name
        storage_account_type  = "Standard_LRS"
        create_option         = "Copy"
        source_resource_id    = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/opera-snapshot-{{SNAPSHOT_DATE}}/providers/Microsoft.Compute/snapshots/{{vm.osdisk}}_{{SNAPSHOT_DATE}}"
        os_type               = "{{vm.ostype}}"

        tags = {
            SNAPSHOT_DATE = var.SNAPSHOT_DATE
            CREATION_DATE = var.CREATION_DATE
            REGION_OWNER_EMAIL = var.REGION_OWNER_EMAIL
            REGION_OWNER    = var.REGION_TRIBE
            REGION_USAGE = var.REGION_USAGE_HOURS
            REGION_CREATED_BY  = var.REGION_CREATED_BY
            REGION_SUBNET  = var.REGION_SUBNET
            CATEGORY           = var.CATEGORY
            PROJECT = var.PROJECT
        }
    }

    {% for vm_datadisk in vm.data_disks -%}
    resource "azurerm_managed_disk" "{{vm_datadisk}}" {
        name                  = "{{vm_datadisk}}"
        location              = azurerm_resource_group.rg.location
        resource_group_name   = azurerm_resource_group.rg.name
        storage_account_type  = "Standard_LRS"
        create_option         = "Copy"
        source_resource_id    = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/opera-snapshot-{{SNAPSHOT_DATE}}/providers/Microsoft.Compute/snapshots/{{vm_datadisk}}_{{SNAPSHOT_DATE}}"
        os_type               = "{{vm.ostype}}"

        tags = {
            SNAPSHOT_DATE = var.SNAPSHOT_DATE
            CREATION_DATE = var.CREATION_DATE
            REGION_OWNER_EMAIL = var.REGION_OWNER_EMAIL
            REGION_OWNER    = var.REGION_TRIBE
            REGION_CREATED_BY  = var.REGION_CREATED_BY
            CATEGORY           = var.CATEGORY
            PROJECT = var.PROJECT
            REGION_SUBNET  = var.REGION_SUBNET
            REGION_USAGE = var.REGION_USAGE_HOURS
        }
    }
    
    {% endfor %}
{% endfor %}
