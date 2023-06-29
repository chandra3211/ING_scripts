terraform {
  backend "azurerm" {
    resource_group_name  = "terraform"
    storage_account_name = "operaregions"
    container_name       = "biab-regions"
    key                  = "{{region_name}}.tfstate"
  }
}
