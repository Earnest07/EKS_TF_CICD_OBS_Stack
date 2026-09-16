module "ecr" {
  source = "../../modules/ecr"

  repository_name = var.ecr_repository_name
  environment     = var.environment
}

module "vpc" {
  source = "../../modules/vpc"

  vpc_name = "eks-cicd-vpc"
  vpc_cidr = "10.0.0.0/16"

  availability_zones = [
    "ap-south-1a",
    "ap-south-1b"
  ]

  public_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]

  private_subnet_cidrs = [
    "10.0.11.0/24",
    "10.0.12.0/24"
  ]

  environment = "eks"
}

module "eks" {
  source = "../../modules/eks"

  cluster_name = "eks-cicd"

  vpc_id = module.vpc.vpc_id

  private_subnet_ids = module.vpc.private_subnet_ids

  environment = "eks"

  kubernetes_version = "1.33"

  node_instance_types = [
    "t3.small"
  ]

  node_desired_size = 1
  node_min_size     = 1
  node_max_size     = 2
}