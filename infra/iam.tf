data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# Execution role: used by the ECS agent itself to pull the image from ECR,
# write logs to CloudWatch, and fetch the secrets referenced in the task
# definition's `secrets` block.
resource "aws_iam_role" "ecs_execution" {
  name               = "${var.project}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "ecs_execution_secrets" {
  statement {
    actions = ["secretsmanager:GetSecretValue"]
    resources = [
      aws_secretsmanager_secret.database_url.arn,
      aws_secretsmanager_secret.jwt_secret_key.arn,
      aws_secretsmanager_secret.openai_api_key.arn,
    ]
  }
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name   = "${var.project}-ecs-execution-secrets"
  role   = aws_iam_role.ecs_execution.id
  policy = data.aws_iam_policy_document.ecs_execution_secrets.json
}

# Task role: used by the running application code (boto3 inside the
# container) -- scoped to exactly the one S3 bucket and one SQS queue this
# app uses. No static AWS_ACCESS_KEY_ID/SECRET needed anywhere; boto3 picks
# this up automatically from the container's credentials provider chain.
resource "aws_iam_role" "ecs_task" {
  name               = "${var.project}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json
}

data "aws_iam_policy_document" "ecs_task_app" {
  statement {
    sid       = "S3ResumeStorage"
    actions   = ["s3:PutObject", "s3:GetObject"]
    resources = ["${aws_s3_bucket.resumes.arn}/*"]
  }

  statement {
    sid       = "SQSEvaluationQueue"
    actions   = ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.evaluation_jobs.arn, aws_sqs_queue.evaluation_jobs_dlq.arn]
  }
}

resource "aws_iam_role_policy" "ecs_task_app" {
  name   = "${var.project}-ecs-task-app"
  role   = aws_iam_role.ecs_task.id
  policy = data.aws_iam_policy_document.ecs_task_app.json
}
