data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_caller_identity" "current" {}

# Resolves to whatever the latest available Postgres 16.x minor version is
# in this account/region at apply time, rather than hardcoding a minor
# version string that may not exist by the time this runs.
data "aws_rds_engine_version" "postgres16" {
  engine  = "postgres"
  version = "16"
}

