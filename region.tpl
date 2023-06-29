data "azurerm_client_config" "current" {}

resource "azurerm_resource_group" "rg" {
  location = var.AZURE_LOCATION
  name     = "region_${var.REGION_NAME}"
  
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

data "azurerm_virtual_network" "opera_static_network" {
  name                = var.HUB_VNET_NAME
  resource_group_name = "{{hub.getname()}}"
}

resource "azurerm_subnet" "region_subnet" {
  resource_group_name       = "{{hub.getname()}}"
  virtual_network_name      = data.azurerm_virtual_network.opera_static_network.name
  name                      = "${var.REGION_NAME}_subnet"
  address_prefix            = "{{region_subnet}}"
}

data "azurerm_network_security_group" "nsg_biab" {
  resource_group_name           = "{{hub.getname()}}"
  name                          = "nsg_biab"
}

resource "azurerm_subnet_network_security_group_association" "nsga" {
  subnet_id                 = azurerm_subnet.region_subnet.id
  network_security_group_id = data.azurerm_network_security_group.nsg_biab.id
}
