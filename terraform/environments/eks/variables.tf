variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "ecr_repository_name" {
  description = "ECR repository name"
  type        = string
  default     = "eks-cicd-demo"
}