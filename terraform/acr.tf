resource "azurerm_container_registry" "gallery" {
  name                = "galleryProject"
  resource_group_name = "ressource"
  location            = "norwayeast"
  sku                 = "Basic"

  # Match the existing settings for the initial import.
  admin_enabled                = true
  public_network_access_enabled = true
}
