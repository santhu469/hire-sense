"""
Generates docs/architecture/diagrams/process_flow.png

The primary HireSense application flow, as defined in the Business
Requirements Document section 2, with the two non-negotiable human-in-the-
loop gates called out explicitly (AI never finalizes a hiring decision;
outbound email always requires an explicit human send action).

Run from the repo root with the project venv:
    docs/.venv/bin/python docs/architecture/scripts/process_flow.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.generic.blank import Blank

OUT_DIR = "docs/architecture/diagrams"

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "pad": "0.4",
    "splines": "spline",
    "nodesep": "0.6",
    "ranksep": "0.9",
}

with Diagram(
    "HireSense - Primary Application Flow",
    filename=f"{OUT_DIR}/process_flow",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
):
    login = Blank("1. Login\n(email/password, RBAC)")
    jd = Blank("2. Create / Upload JD\n(manual, upload, or AI-generated)")
    upload = Blank("3. Upload Resumes\n(bulk, 10-100+ per JD)")

    with Cluster("4. AI Evaluation (async, queued)"):
        evaluate = Blank("Score every candidate\nvs. JD (weighted categories)")
        insights = Blank("Generate explainable\ninsights per candidate")
        evaluate >> insights

    ranking = Blank("5. Candidate Ranking\n(Top 10 + full list,\nfilter / sort)")

    with Cluster("6. Human Decision  <-- AI cannot do this step"):
        decision = Blank("Recruiter sets status:\nShortlisted | Hold | Rejected\n(history logged)")

    with Cluster("7. Communication  <-- send always requires a human click"):
        draft = Blank("AI drafts email\n(shortlist / hold / reject /\ninterview next-step)")
        send = Blank("Human reviews &\nexplicitly sends")
        draft >> Edge(label="approve") >> send

    login >> jd >> upload >> evaluate
    insights >> ranking >> decision >> draft
