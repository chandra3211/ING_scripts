variable "HUB_RG_NAME" {
  description = "The name of the resource group containing the hub"
  type        = string
  default     = "{{hub.getname()}}"
}

variable "HUB_VNET_NAME" {
  description = "The name of the hub's vnet"
  type        = string
  default     = "{{hub.getvnet()}}" 
}

variable "REGION_SUBNET" {
  description = "The name of the subnet"
  type        = string
  default     = "{{hub.getsubnet()}}" 
}

variable "AZURE_LOCATION" {
  description = "The Azure location in which to provision this region"
  type        = string
  default     = "Australia East"
}

variable "REGION_NAME" {
  description = "The name assigned to this region"
  type        = string
  default     = "{{region_name}}"
}

variable "SNAPSHOT_DATE" {
  description = "The date of the snapshots"
  type        = string
  default     = "{{SNAPSHOT_DATE}}"
}

variable "CREATION_DATE" {
  description = "The creation date of the region"
  type        = string
  default     = "{{creation_date}}"
}

variable "REGION_OWNER_EMAIL" {
  description = "The owner's email of resource group"
  type        = string
  default     = "releaseteam@ing.com.au"
}

variable "REGION_TRIBE" {
  description = "The location of resource group"
  type        = string
  default     = "OTHERS"
}

variable "REGION_USAGE_HOURS" {
  description = "The usage period in hours"
  type        = string
  default     = "NONE"
}

variable "REGION_CREATED_BY" {
  description = "The DevOps resource creating this region"
  type        = string
  default     = "DEVOPS"
}

variable "CATEGORY" {
  description = "The type of region e.g. BIAB"
  type        = string
  default     = "BIAB"
}

variable "PROJECT" {
  description = "The project owns the region"
  type        = string
  default     = "OTHERS"
}

variable "boot_storageaccount"{
  description = "The storage account for BIAB boot diagrostix"
  type        = string
  default     = "biabbootdiag"
}
