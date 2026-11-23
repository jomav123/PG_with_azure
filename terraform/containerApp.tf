resource "azurerm_container_app" "gallery" {
  name                         = "jocontainer"
  resource_group_name          = "ressource"
  container_app_environment_id = azurerm_container_app_environment.gallery.id
  revision_mode                = "Single"

  ingress {
    external_enabled = true
    target_port      = 5000
    transport        = "auto"

  traffic_weight {
    latest_revision = true
     percentage      = 100
    }
  }
  workload_profile_name     = "Consumption"
  max_inactive_revisions    = 100

  template {
    min_replicas = 0
    max_replicas = 10

    container {
      name   = "jocontainer"
      image  = "galleryproject.azurecr.io/pgwsb-app:v1"
      cpu    = 1
      memory = "2Gi"  
      liveness_probe {
        transport               = "TCP"
        port                    = 5000
        failure_count_threshold = 3
        initial_delay           = 0
        interval_seconds        = 10
        timeout                 = 5
      }

      readiness_probe {
        transport               = "TCP"
        port                    = 5000
        failure_count_threshold = 48
        initial_delay           = 0
        interval_seconds        = 5
        success_count_threshold = 1
        timeout                 = 5
      }

      startup_probe {
        transport               = "TCP"
        port                    = 5000
        failure_count_threshold = 240
        initial_delay           = 1
        interval_seconds        = 1
        timeout                 = 3
      }
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
