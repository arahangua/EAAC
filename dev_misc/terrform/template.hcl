provider "kubernetes" {
  # Configuration for Kubernetes provider
  config_path    = "~/.kube/config"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "kubernetes_namespace" "db_namespace" {
  metadata {
    name = "database-namespace"
  }
}


resource "helm_release" "my_database" {
  name       = "my-database"
  namespace  = kubernetes_namespace.db_namespace.metadata[0].name
  repository = "https://github.com/DozerDB/helm-charts"
  chart      = "dozerdb"
  version    = "1.2.3"

  set {
    name  = "cluster.enabled"
    value = "true"
  }

  set {
    name  = "cluster.coreMembers"
    value = "3"
  }

  set {
    name  = "cluster.readReplicas"
    value = "2"
  }
}


#terraform init  # Initializes Terraform, downloads provider plugins, etc.
#terraform apply # Applies the configurations
