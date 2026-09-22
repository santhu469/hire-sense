"""
Generates docs/architecture/diagrams/data_model_er.png

Entity-relationship diagram for the HireSense core data model. Built with
the raw `graphviz` Python binding (HTML-like record labels) rather than the
`diagrams` library, since `diagrams` is aimed at infra/component diagrams,
not ER layouts.

Run from the repo root with the project venv:
    docs/.venv/bin/python docs/architecture/scripts/data_model_er.py
"""

import graphviz

OUT_DIR = "docs/architecture/diagrams"

# (entity_name, [(field, tag)]) — tag is "PK", "FK", or "" for a plain field.
ENTITIES = {
    "User": [
        ("id", "PK"),
        ("email", ""),
        ("password_hash", ""),
        ("role", "Admin/Recruiter/Viewer"),
        ("created_at", ""),
    ],
    "JobDescription": [
        ("id", "PK"),
        ("title", ""),
        ("raw_text", ""),
        ("structured_requirements", "JSONB"),
        ("status", ""),
        ("created_by", "FK: User"),
        ("created_at", ""),
    ],
    "EvaluationCriteria": [
        ("id", "PK"),
        ("jd_id", "FK: JobDescription"),
        ("category", ""),
        ("weight", ""),
        ("version", ""),
    ],
    "Candidate": [
        ("id", "PK"),
        ("jd_id", "FK: JobDescription"),
        ("resume_file_url", ""),
        ("raw_text", ""),
        ("parsed_profile", "JSONB"),
        ("current_status", "Shortlisted/Hold/Rejected"),
        ("uploaded_at", ""),
    ],
    "Evaluation": [
        ("id", "PK"),
        ("candidate_id", "FK: Candidate"),
        ("jd_id", "FK: JobDescription"),
        ("criteria_version", ""),
        ("overall_score", ""),
        ("category_scores", "JSONB"),
        ("insights", "JSONB"),
        ("is_latest", "bool"),
        ("created_at", ""),
    ],
    "CandidateDecision": [
        ("id", "PK"),
        ("candidate_id", "FK: Candidate"),
        ("jd_id", "FK: JobDescription"),
        ("status", "Shortlisted/Hold/Rejected"),
        ("changed_by", "FK: User"),
        ("changed_at", ""),
        ("reason_note", ""),
    ],
    "EmailDraft": [
        ("id", "PK"),
        ("candidate_id", "FK: Candidate"),
        ("template_type", ""),
        ("subject", ""),
        ("body", ""),
        ("status", "draft/sent"),
        ("approved_by", "FK: User"),
        ("sent_at", ""),
    ],
}

# (from_entity, to_entity, cardinality_label)
RELATIONSHIPS = [
    ("User", "JobDescription", "1 creates N"),
    ("JobDescription", "EvaluationCriteria", "1 defines N"),
    ("JobDescription", "Candidate", "1 has N"),
    ("Candidate", "Evaluation", "1 has N (versioned)"),
    ("JobDescription", "Evaluation", "1 has N"),
    ("Candidate", "CandidateDecision", "1 has N (audit log)"),
    ("User", "CandidateDecision", "1 changes N"),
    ("Candidate", "EmailDraft", "1 has N"),
    ("User", "EmailDraft", "1 approves N"),
]


def entity_html_label(name, fields):
    rows = [
        f'<TR><TD BGCOLOR="#1f4e79" ALIGN="CENTER"><FONT COLOR="white"><B>{name}</B></FONT></TD></TR>'
    ]
    for field, tag in fields:
        if tag in ("PK",):
            text = f'<B>{field}</B>  <FONT COLOR="#b02b2b">[{tag}]</FONT>'
        elif tag.startswith("FK"):
            text = f'{field}  <FONT COLOR="#1f6f43">[{tag}]</FONT>'
        elif tag:
            text = f'{field}  <FONT COLOR="#666666" POINT-SIZE="10">({tag})</FONT>'
        else:
            text = field
        rows.append(f'<TR><TD ALIGN="LEFT">{text}</TD></TR>')
    return (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">'
        + "".join(rows)
        + "</TABLE>>"
    )


def build():
    g = graphviz.Digraph(
        "HireSense_Data_Model",
        format="png",
        graph_attr={
            "rankdir": "LR",
            "splines": "ortho",
            "fontsize": "22",
            "label": "HireSense - Core Data Model (ER Diagram)",
            "labelloc": "t",
            "bgcolor": "white",
            "nodesep": "0.5",
            "ranksep": "0.9",
        },
        node_attr={"shape": "plaintext"},
        edge_attr={"fontsize": "10", "color": "#555555"},
    )

    for name, fields in ENTITIES.items():
        g.node(name, label=entity_html_label(name, fields))

    for src, dst, label in RELATIONSHIPS:
        g.edge(src, dst, label=label)

    g.render(filename=f"{OUT_DIR}/data_model_er", cleanup=True)


if __name__ == "__main__":
    build()
