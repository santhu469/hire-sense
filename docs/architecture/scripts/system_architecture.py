"""
Generates docs/architecture/diagrams/system_architecture.png

Logical / component-level view of HireSense — cloud-agnostic, shows the
application services and how they talk to each other and to shared
infrastructure. For the concrete AWS deployment topology see
aws_deployment.py instead.

Run from the repo root with the project venv:
    docs/.venv/bin/python docs/architecture/scripts/system_architecture.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.programming.framework import React, Fastapi
from diagrams.onprem.database import PostgreSQL
from diagrams.aws.storage import S3
from diagrams.aws.integration import SQS
from diagrams.generic.blank import Blank

OUT_DIR = "docs/architecture/diagrams"

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
}

with Diagram(
    "HireSense - System Architecture",
    filename=f"{OUT_DIR}/system_architecture",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    user = Users("Recruiter /\nHiring Manager /\nAdmin")

    with Cluster("Client"):
        frontend = React("Next.js Frontend\n(TypeScript, SSR)")

    with Cluster("API Layer"):
        gateway = Fastapi("API Gateway / BFF\n(Auth, RBAC, routing)")

    with Cluster("Application Services (FastAPI, Python)"):
        jd_service = Blank("JD Service\n(create / upload /\nAI generate)")
        ingestion = Blank("Resume Ingestion\nService\n(bulk upload, parse)")
        evaluator = Blank("Evaluation\nOrchestrator\n(async scoring jobs)")
        ranking = Blank("Ranking &\nShortlisting Service")
        decision = Blank("Decision & Audit\nService")
        comms = Blank("Communication\nService\n(draft -> approve -> send)")

    with Cluster("Async Processing"):
        queue = SQS("Evaluation Job Queue")
        worker = Blank("Evaluation Worker\n(background jobs)")

    with Cluster("Shared Data"):
        db = PostgreSQL("PostgreSQL\n(JDs, candidates,\nscores, decisions,\nusers, audit log)")
        storage = S3("Object Storage\n(resume files)")

    llm = Blank("Claude API\n(Anthropic)\n[external]")
    email = Blank("Email Provider\n(SES)\n[external]")

    user >> frontend >> gateway
    gateway >> Edge(color="gray40") >> jd_service
    gateway >> Edge(color="gray40") >> ingestion
    gateway >> Edge(color="gray40") >> ranking
    gateway >> Edge(color="gray40") >> decision
    gateway >> Edge(color="gray40") >> comms

    ingestion >> Edge(label="store resume") >> storage
    ingestion >> Edge(label="enqueue eval job") >> queue
    queue >> worker >> Edge(label="score candidate") >> llm
    worker >> Edge(label="write Evaluation") >> db
    evaluator >> Edge(style="dashed", label="weighted rescoring\n(no LLM call)") >> db

    jd_service >> db
    ranking >> db
    decision >> db
    comms >> Edge(label="draft via LLM") >> llm
    comms >> Edge(label="human-approved send only") >> email
    comms >> db
