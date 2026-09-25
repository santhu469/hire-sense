# HireSense AWS infrastructure

Terraform for the real target architecture from the root `CLAUDE.md`:
ECS Fargate (backend API, worker, frontend — three services, two images,
since the backend image serves both API and worker via `PROCESS_TYPE`),
RDS Postgres, S3, SQS, ALB, ECR, Secrets Manager, CloudWatch.

**Scoped as a first pass, not gold-plated** — see the bottom of this file
for what's deliberately deferred.

## Setup

```bash
aws configure --profile hiresense   # if not already done
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: set openai_api_key to a real key
terraform init
terraform plan     # review the full resource list + look at the cost
                    # estimate in the root plan before applying
terraform apply
```

## First deploy

`terraform apply` creates the ECR repos and ECS services, but the services
will crash-loop until images actually exist. After `apply` succeeds:

```bash
./build_and_push.sh
```

This builds `backend/` and `frontend/`, pushes both to ECR, and forces a
new deployment on all three ECS services.

## Running the database migration

The ECS services don't run migrations automatically. After the first
`build_and_push.sh`, run Alembic once against the new RDS instance via a
one-off Fargate task using the same image/network/secrets as the real
services:

```bash
CLUSTER=$(terraform output -raw ecs_cluster_name)

aws ecs run-task \
  --cluster "$CLUSTER" \
  --task-definition hiresense-backend-api \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-id>],securityGroups=[<ecs-tasks-sg-id>],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"backend","command":["sh","-c","uv run alembic upgrade head"]}]}' \
  --profile hiresense --region "$(terraform output -raw aws_region)"
```

Get the exact subnet/security-group IDs from `terraform state show
aws_security_group.ecs_tasks` and `data.aws_subnets.default` (or just
`terraform console`). Tail the result in CloudWatch under
`/ecs/hiresense-backend-api`.

## Redeploying after a code change

```bash
./build_and_push.sh
```

## Tearing down

```bash
terraform destroy
```

Removes everything — do this between sessions if you want to avoid the
~$70–90/month running cost estimated in the root plan. `desired_count` on
any `aws_ecs_service` can also be scaled to 0 (`terraform apply
-var desired_count=0` — not currently a variable, edit `ecs.tf` directly
or use `aws ecs update-service --desired-count 0`) for a cheaper pause
without losing the RDS data.

## Deliberately deferred

- Custom domain + HTTPS/ACM cert — the ALB is HTTP-only right now.
- RDS Multi-AZ — single-AZ to halve that cost; flip `multi_az = true` in
  `rds.tf` when ready.
- Private subnets + NAT gateway — using the default VPC's public subnets
  with tightly scoped security groups instead; RDS is `publicly_accessible
  = false` regardless.
- CI/CD — `build_and_push.sh` is run by hand; GitHub Actions is real
  future work, not done here.
- Remote Terraform state (S3 backend + DynamoDB lock table) — state is
  local (`infra/*.tfstate`, gitignored). Fine solo; revisit before anyone
  else touches this.
