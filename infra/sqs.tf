resource "aws_sqs_queue" "evaluation_jobs_dlq" {
  name = "${var.project}-evaluation-jobs-dlq"

  tags = { Project = var.project }
}

resource "aws_sqs_queue" "evaluation_jobs" {
  name                       = "${var.project}-evaluation-jobs"
  visibility_timeout_seconds = 120 # generous margin over one resume's parse+score time

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.evaluation_jobs_dlq.arn
    maxReceiveCount     = 5
  })

  tags = { Project = var.project }
}
