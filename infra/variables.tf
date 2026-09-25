variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use (set up via `aws configure --profile <name>`)"
  type        = string
  default     = "hiresense"
}

variable "project" {
  type    = string
  default = "hiresense"
}

variable "openai_api_key" {
  description = "Real OpenAI API key -- supply via terraform.tfvars (gitignored) or TF_VAR_openai_api_key, never commit it"
  type        = string
  sensitive   = true
}

variable "openai_model" {
  type    = string
  default = "gpt-4o-mini"
}

variable "backend_image_tag" {
  description = "Image tag to deploy for the backend/worker ECR repo (updated by infra/build_and_push.sh)"
  type        = string
  default     = "latest"
}

variable "frontend_image_tag" {
  description = "Image tag to deploy for the frontend ECR repo (updated by infra/build_and_push.sh)"
  type        = string
  default     = "latest"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_allocated_storage_gb" {
  type    = number
  default = 20
}

variable "fargate_cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU) -- same size for all three services in this first pass"
  type        = string
  default     = "256"
}

variable "fargate_memory" {
  description = "Fargate task memory in MB (512 = 0.5 GB)"
  type        = string
  default     = "512"
}
