resource "random_password" "db" {
  length  = 32
  special = false # keep it URL-safe since it goes straight into a connection string
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-db"
  subnet_ids = data.aws_subnets.default.ids

  tags = { Project = var.project }
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project}-db"
  engine         = "postgres"
  engine_version = data.aws_rds_engine_version.postgres16.version

  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage_gb
  storage_type           = "gp3"
  db_name                = "hiresense"
  username               = "hiresense"
  password               = random_password.db.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az                = false # single-AZ for this first pass, see infra/README.md
  publicly_accessible     = false
  storage_encrypted       = true
  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 1

  tags = { Project = var.project }
}
