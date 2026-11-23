resource "azurerm_container_app_environment" "gallery" {
  name                = "managedEnvironment-ressource-8524"
  resource_group_name = "ressource"
  location            = "norwayeast"

  logs_destination = "azure-monitor"

  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
  
  identity {
    type = "SystemAssigned"
  }
}
