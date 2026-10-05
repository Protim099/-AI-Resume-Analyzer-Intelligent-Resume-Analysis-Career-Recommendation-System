"""Downloadable PDF analysis report (ReportLab)."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..ai.ats_scorer import grade

BRAND = colors.HexColor("#0f766e")


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_report(data: dict, user_name: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                            bottomMargin=16 * mm, title="Resume Analysis Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=BRAND, fontSize=20, alignment=0)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=BRAND, spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("s", parent=body, textColor=colors.grey, fontSize=8.5)
    el = [Paragraph("AI Resume Analysis Report", h1),
          Paragraph(f"Prepared for {_esc(user_name)} &bull; {datetime.now():%d %b %Y %H:%M} &bull; Resume: "
                    f"{_esc(data['resume_filename'])}", small), Spacer(1, 6)]

    rows = [["ATS Score", f"{data['ats_score']:.0f} / 100  ({grade(data['ats_score'])})"]]
    if data.get("job_match_score") is not None:
        rows += [["Job", _esc(data.get("job_title"))], ["Job Match Score", f"{data['job_match_score']:.1f}%"],
                 ["Skill / Semantic / Keyword", f"{data.get('skill_match_score') or 0:.0f}% / {data.get('semantic_score') or 0:.0f}% / {data.get('keyword_score') or 0:.0f}%"]]
    t = Table(rows, colWidths=[55 * mm, 115 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecfdf5")), ("FONTSIZE", (0, 0), (-1, -1), 10),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey), ("PADDING", (0, 0), (-1, -1), 5)]))
    el += [t, Paragraph("ATS Score Breakdown", h2)]
    bt = Table([["Category", "Score", "Max"]] + [[k, v["score"], v["max"]] for k, v in data["ats_breakdown"].items()],
               colWidths=[90 * mm, 40 * mm, 40 * mm])
    bt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BRAND), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey), ("FONTSIZE", (0, 0), (-1, -1), 9.5)]))
    el.append(bt)

    r = data["resume"]
    c = r["contact"]
    el += [Paragraph("Extracted Profile", h2),
           Paragraph(f"<b>Name:</b> {_esc(c.get('name'))} &nbsp; <b>Email:</b> {_esc(c.get('email'))} &nbsp; "
                     f"<b>Phone:</b> {_esc(c.get('phone'))}", body),
           Paragraph("<b>Skills:</b> " + _esc(", ".join(s["name"] for s in r["skills"]) or "None detected"), body)]
    for e in r["education"]:
        el.append(Paragraph(f"&bull; <b>Education:</b> {_esc(e.get('degree'))} - {_esc(e.get('institution'))} {_esc(e.get('year'))}", body))
    for e in r["experience"]:
        el.append(Paragraph(f"&bull; <b>Experience:</b> {_esc(e['title'])} at {_esc(e['company'])} ({_esc(e['duration'])})", body))
    for p in r["projects"]:
        el.append(Paragraph(f"&bull; <b>Project:</b> {_esc(p['name'])} [{_esc(', '.join(p.get('technologies', [])))}]", body))
    for cert in r["certifications"]:
        el.append(Paragraph(f"&bull; <b>Certification:</b> {_esc(cert)}", body))

    if data.get("has_job_match"):
        el += [Paragraph("Skill Match", h2),
               Paragraph("<b>Matched:</b> " + _esc(", ".join(s["name"] for s in data["matched_skills"]) or "-"), body),
               Paragraph("<b>Missing:</b> " + _esc(", ".join(s["name"] for s in data["missing_skills"]) or "-"), body)]
    el.append(Paragraph("Suggested Job Roles", h2))
    for role in data["suggested_roles"]:
        el.append(Paragraph(f"&bull; {_esc(role['role'])} - {role['match']:.0f}% match", body))
    el.append(Paragraph("Skill Gaps & Learning Path", h2))
    for g in data["learning_path"][:10]:
        el.append(Paragraph(f"&bull; {_esc(g['technology'])} ({g['priority']}) - {_esc(g['reason'])}", body))
    el.append(Paragraph("Recommendations", h2))
    for rec in data["recommendations"]:
        el.append(Paragraph(f"&bull; [{rec['priority'].upper()}] {_esc(rec['text'])}", body))
    doc.build(el)
    return buf.getvalue()
