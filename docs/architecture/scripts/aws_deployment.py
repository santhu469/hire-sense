"""
Generates docs/architecture/diagrams/aws_deployment.png

Concrete AWS deployment topology for HireSense (single-org, single-region
deployment for v1). Frontend and backend both run as containers on ECS
Fargate behind a shared Application Load Balancer; async evaluation jobs
run in a separate Fargate worker service pulling from SQS.

Run from the repo root with the project venv:
    docs/.venv/bin/python docs/architecture/scripts/aws_deployment.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import Route53, ALB, VPC
from diagrams.aws.compute import Fargate, ECR
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS
from diagrams.aws.security import SecretsManager
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.client import Users
from diagrams.generic.blank import Blank

OUT_DIR = "docs/architecture/diagrams"

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
}

with Diagram(
    "HireSense - AWS Deployment Architecture",
    filename=f"{OUT_DIR}/aws_deployment",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    users = Users("Users\n(HTTPS)")
    dns = Route53("Route 53")

    with Cluster("AWS Account - eu/us region"):
        with Cluster("VPC"):
            alb = ALB("Application\nLoad Balancer\n(ACM TLS)")

            with Cluster("Private Subnets - App Tier (ECS Fargate)"):
                fe_svc = Fargate("Frontend Service\n(Next.js SSR)")
                api_svc = Fargate("Backend API Service\n(FastAPI)")
                worker_svc = Fargate("Evaluation Worker\nService (Python)")

            with Cluster("Private Subnets - Data Tier"):
                rds = RDS("RDS PostgreSQL\n(Multi-AZ)")

        queue = SQS("Evaluation\nJob Queue")
        bucket = S3("S3\n(resume files +\nstatic assets)")
        secrets = SecretsManager("Secrets Manager\n(DB creds,\nAnthropic API key)")
        logs = Cloudwatch("CloudWatch\n(logs & metrics)")
        registry = ECR("ECR\n(container images)")

    ses = Blank("Amazon SES\n(email delivery)")
    anthropic = Blank("Anthropic\nClaude API\n[external]")

    users >> dns >> alb
    alb >> Edge(label="/*") >> fe_svc
    alb >> Edge(label="/api/*") >> api_svc

    api_svc >> Edge(label="read/write") >> rds
    api_svc >> Edge(label="upload resumes") >> bucket
    api_svc >> Edge(label="enqueue job") >> queue
    api_svc >> Edge(label="send approved email") >> ses

    queue >> worker_svc
    worker_svc >> Edge(label="score candidate") >> anthropic
    worker_svc >> rds
    worker_svc >> bucket

    for svc in (fe_svc, api_svc, worker_svc):
        svc >> Edge(style="dotted", color="gray50") >> secrets
        svc >> Edge(style="dotted", color="gray50") >> logs
        registry >> Edge(style="dashed", color="gray50", label="image") >> svc
