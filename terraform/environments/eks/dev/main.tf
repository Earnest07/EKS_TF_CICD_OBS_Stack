module "ecr" {
  source = "../../../modules/ecr"

  repository_name = var.ecr_repository_name
  environment     = var.environment
}