resource "azurerm_postgresql_flexible_server_database" "postgres" {
  name      = "postgres"
  server_id = azurerm_postgresql_flexible_server.photogallery.id
  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = true
  }
}
