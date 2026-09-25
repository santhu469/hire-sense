output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "aws_region" {
  value = var.aws_region
}

output "project" {
  value = var.project
}

output "backend_ecr_repository_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_repository_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.resumes.bucket
}

output "sqs_queue_url" {
  value = aws_sqs_queue.evaluation_jobs.url
}
