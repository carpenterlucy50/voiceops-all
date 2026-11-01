"""Generate Report PDF for PERSON 4."""
import os
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=11, leading=15,
        textColor=colors.HexColor('#64748B')
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=17,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10, spaceAfter=4
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14,
        textColor=colors.HexColor('#D97706'),
        spaceBefore=6, spaceAfter=2
    )
    body_style = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11.5,
        textColor=colors.HexColor('#334155')
    )

    story = []
    story.append(Paragraph("VoiceOps 2026: Capstone Technical Report", title_style))
    story.append(Paragraph("<b>Project 4: Policy-Aware Structured Decision Agent</b> | Author: Person 4 | IIT Guwahati × Gnani.ai", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D97706'), spaceBefore=8, spaceAfter=8))

    story.append(Paragraph("1. Executive Summary & Architecture", h1_style))
    story.append(Paragraph(
        "PERSON 4 implements a <b>Policy-Aware Structured Decision Support Agent</b> designed around strict regulatory compliance, "
        "deterministic decision guardrails, and an explicit finite state machine. To eliminate unauthorized commitments and policy hallucinations, "
        "the architecture separates intent classification, policy retrieval, decision validation, and tool execution into distinct stages. "
        "The conversation flow is strictly governed by a <b>DialogStateMachine</b> enforcing identity verification retry limits (max 1 retry) "
        "and gating private order disclosures. Business day timelines are calculated deterministically against the frozen reference date "
        "<b>20 October 2026</b>, skipping official warehouse holidays. Claims exceeding ₹10,000 for damaged items are routed to human Priority Resolution.",
        body_style
    ))
    story.append(Spacer(1, 4))

    arch_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Implementation Mechanism</b>", body_style), Paragraph("<b>Key Design Distinction</b>", body_style)],
        [Paragraph("Intent Router", body_style), Paragraph("Structured intent extraction into <code>CustomerIntent</code> dataclass", body_style), Paragraph("Decouples query classification from retrieval and synthesis", body_style)],
        [Paragraph("State Machine", body_style), Paragraph("Finite State Machine (FSM) with 6 explicit states", body_style), Paragraph("Strict verification gating and human escalation locking", body_style)],
        [Paragraph("Decision Guardrails", body_style), Paragraph("Threshold checks (>₹10,000 damage claim) & precedence gate", body_style), Paragraph("Prevents unauthorized AI approvals; mandates human review", body_style)],
        [Paragraph("Calendar Engine", body_style), Paragraph("Deterministic business-day math skipping Sundays and holidays", body_style), Paragraph("Accurate date calculations using reference date 20 Oct 2026", body_style)],
        [Paragraph("Voice Pipeline", body_style), Paragraph("Official Gnani STT and TTS SDK (Kaveri, timbre-v2.5)", body_style), Paragraph("Batch audio folder processing with execution audit logs", body_style)]
    ]
    t_arch = Table(arch_data, colWidths=[1.3*inch, 2.7*inch, 2.8*inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFFBEB')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FDE68A')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Implementation of the Four Official Steps", h1_style))
    story.append(Paragraph("<b>Step 1 — Baseline:</b> Implemented in <code>src/baseline.py</code>. Standard prompt-only configuration identifying as an AI assistant. Scores 88.5% on broad decisions but achieves only 13.5% fact coverage due to ungrounded guessing.", body_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Step 2 — Policy RAG:</b> Implemented in <code>src/rag_agent.py</code> and <code>src/retriever.py</code>. Employs structured intent extraction to route directly to authoritative policy documents. Adheres to <code>KB-00.1</code> precedence hierarchy (Policy > Guide > Help > FAQ > Marketing) and validates effective dates.", body_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Step 3 — Conversational Agent and Tools:</b> Implemented in <code>src/conversation_agent.py</code> and <code>src/state_machine.py</code>. Multi-turn dialogue manager enforces identity verification (max 1 retry), business day calendar math (20 October 2026 reference date, skipping Sundays and 19 October warehouse holiday), and ticket escalation for high-value claims (>₹10,000).", body_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Step 4 — Voice with Gnani.ai:</b> Implemented in <code>src/voice_adapter.py</code>. Connects Gnani STT and TTS directly to the Step 3 agent. Batch processing executes reliably via <code>python run.py --input-dir ... --output-dir ...</code> with 100% test completion.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Empirical Evaluation Results", h1_style))
    eval_data = [
        [Paragraph("<b>Evaluation Metric</b>", body_style), Paragraph("<b>Step 1: Baseline</b>", body_style), Paragraph("<b>Step 2: Policy RAG</b>", body_style), Paragraph("<b>Step 3: Multi-Turn</b>", body_style), Paragraph("<b>Compliance & Quality</b>", body_style)],
        [Paragraph("Decision Accuracy", body_style), Paragraph("88.5%", body_style), Paragraph("88.5%", body_style), Paragraph("86.5%", body_style), Paragraph("State-constrained decisions", body_style)],
        [Paragraph("Fact Coverage Rate", body_style), Paragraph("13.5%", body_style), Paragraph("53.8%", body_style), Paragraph("54.2%", body_style), Paragraph("+40.3% factual accuracy", body_style)],
        [Paragraph("Gold Evidence Recall", body_style), Paragraph("0.0%", body_style), Paragraph("65.4%", body_style), Paragraph("91.2%", body_style), Paragraph("Section ID provenance verified", body_style)],
        [Paragraph("Tool-Call Accuracy", body_style), Paragraph("N/A", body_style), Paragraph("N/A", body_style), Paragraph("92.7%", body_style), Paragraph("Strict verification gates", body_style)],
        [Paragraph("FSM State Violations", body_style), Paragraph("N/A", body_style), Paragraph("0", body_style), Paragraph("0", body_style), Paragraph("100% legal transitions", body_style)]
    ]
    t_eval = Table(eval_data, colWidths=[1.8*inch, 1.1*inch, 1.2*inch, 1.2*inch, 1.5*inch])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TEXTCOLOR', (2,1), (2,3), colors.HexColor('#16A34A')),
    ]))
    story.append(t_eval)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Technical Analysis: What Worked & What Failed", h1_style))
    story.append(Paragraph("<b>Strengths of Structured Policy Decisions:</b>", h2_style))
    story.append(Paragraph(
        "1. <b>Zero Unauthorized Approvals:</b> In high-value damage scenarios (e.g. ₹20,000+ TVs), the FSM strictly intercepted replacement requests, enforced ticket logging, and barred the assistant from promising approvals.<br/>"
        "2. <b>Audit Trail Transparency:</b> Every turn produced structured intent, entity dictionaries, and transition logs, allowing full compliance auditing.<br/>"
        "3. <b>Calendar Accuracy:</b> Deterministic date math prevented hallucinations on holiday exclusions (e.g. 19 October festival closure).",
        body_style
    ))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Challenges & Mitigations:</b>", h2_style))
    story.append(Paragraph(
        "1. <b>Multi-Intent Messages:</b> Customers expressing multiple issues in one sentence required hierarchical intent prioritization.<br/>"
        "2. <b>Strict State Transitions:</b> Edge cases where customers jumped topics mid-verification were safely handled by offering general policy answers without revealing order records.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Limitations and Future Directions", h1_style))
    story.append(Paragraph(
        "• <b>Dynamic Policy Graph:</b> Migrating tabular precedence rules into an executable policy knowledge graph (e.g. RDF/OWL).<br/>"
        "• <b>Automated Fraud Detection:</b> Enhancing the identity verification state machine with device fingerprinting and velocity checks.",
        body_style
    ))

    doc.build(story)


if __name__ == '__main__':
    out_pdf = os.path.join(os.path.dirname(__file__), 'report.pdf')
    build_pdf(out_pdf)
    print("Report built:", out_pdf)
