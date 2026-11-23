variable "postgres_administrator_password" {
  type      = string
  sensitive = true
}

resource "azurerm_postgresql_flexible_server" "photogallery" {
  name                = "photogallery"
  resource_group_name = "ressource"
  location            = "Norway East"

  administrator_login    = "jopostgre"
  administrator_password = var.postgres_administrator_password
  version                = "18"
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
  zone = "3"

  public_network_access_enabled = true

  lifecycle {
    ignore_changes = [administrator_password]
  }
}
