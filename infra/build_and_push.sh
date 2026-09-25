#!/usr/bin/env bash
# Builds backend/ and frontend/, pushes both to their ECR repos, and forces
# a new deployment on all three ECS services. Run after `terraform apply`
# has created the ECR repos (and again for every code change, until CI/CD
# exists).
set -euo pipefail

AWS_PROFILE="${AWS_PROFILE:-hiresense}"
INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$INFRA_DIR/.." && pwd)"

cd "$INFRA_DIR"
AWS_REGION="$(terraform output -raw aws_region)"
PROJECT="$(terraform output -raw project)"
BACKEND_REPO="$(terraform output -raw backend_ecr_repository_url)"
FRONTEND_REPO="$(terraform output -raw frontend_ecr_repository_url)"
CLUSTER="$(terraform output -raw ecs_cluster_name)"

echo "==> Logging into ECR ($AWS_REGION, profile $AWS_PROFILE)"
aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" \
  | docker login --username AWS --password-stdin "$BACKEND_REPO"

echo "==> Building backend (shared by the API and worker services)"
# --platform linux/amd64: Fargate tasks default to X86_64, but this may be
# built on an Apple Silicon Mac, which produces arm64 images by default.
docker build --platform linux/amd64 -t "$BACKEND_REPO:latest" "$ROOT_DIR/backend"
docker push "$BACKEND_REPO:latest"

echo "==> Building frontend"
docker build --platform linux/amd64 -t "$FRONTEND_REPO:latest" "$ROOT_DIR/frontend"
docker push "$FRONTEND_REPO:latest"

echo "==> Forcing new ECS deployments"
for service in "$PROJECT-backend-api" "$PROJECT-worker" "$PROJECT-frontend"; do
  aws ecs update-service \
    --cluster "$CLUSTER" \
    --service "$service" \
    --force-new-deployment \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" \
    --no-cli-pager \
    >/dev/null
  echo "   redeployed $service"
done

echo "==> Done. Watch rollout with:"
echo "    aws ecs describe-services --cluster $CLUSTER --services $PROJECT-backend-api --profile $AWS_PROFILE --region $AWS_REGION"
