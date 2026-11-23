resource "azurerm_container_app" "gallery" {
  name                         = "jocontainer"
  resource_group_name          = "ressource"
  container_app_environment_id = azurerm_container_app_environment.gallery.id
  revision_mode                = "Single"

  ingress {
    external_enabled = true
    target_port      = 5000
    transport        = "auto"
  }

  template {
    min_replicas = 0
    max_replicas = 10

    container {
      name   = "jocontainer"
      image  = "galleryproject.azurecr.io/pgwsb-app:v1"
      cpu    = 1
      memory = "2Gi"

      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }

      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "pdb-password"
      }

      env {
        name  = "POSTGRES_USER"
        value = "jopostgre"
      }

      env {
        name  = "POSTGRES_DB"
        value = "postgres"
      }

      env {
        name  = "POSTGRES_PORT"
        value = "5432"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      registry,
      secret,
    ]
  }
}
