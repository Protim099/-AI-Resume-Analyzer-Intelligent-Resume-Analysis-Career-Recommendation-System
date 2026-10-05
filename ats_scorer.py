"""ATS resume scoring (0-100) with a transparent, weighted breakdown."""
import re

from .skills_db import SKILL_CATEGORIES

ACTION_VERBS = {
    "achieved", "analyzed", "architected", "automated", "built", "collaborated", "configured", "created",
    "debugged", "delivered", "deployed", "designed", "developed", "enhanced", "engineered", "established",
    "implemented", "improved", "increased", "integrated", "launched", "led", "maintained", "managed",
    "migrated", "mentored", "optimized", "orchestrated", "organized", "reduced", "refactored", "researched",
    "resolved", "scaled", "secured", "streamlined", "tested", "trained", "transformed", "wrote", "coordinated",
    "initiated", "executed", "evaluated", "modeled", "programmed", "published", "presented", "supervised",
}
WEAK_PHRASES = ["responsible for", "worked on", "duties included", "helped with", "hardworking", "team player",
                "go-getter", "detail oriented", "references available"]
QUANT_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|percent|x|k|m|users|customers|requests|ms|seconds|hours|"
                      r"projects|models|apis|clients|members|students)\b|\$\s?\d+|\b\d{2,}\+?\b", re.I)


def _pts(value: float, maximum: float) -> float:
    return round(max(0.0, min(value, maximum)), 1)


def score_resume(parsed: dict, text: str, meta: dict) -> dict:
    contact, counts = parsed["contact"], parsed["counts"]
    sections = set(parsed["sections_found"])
    skills = parsed["skills"]
    tech = [s for s in skills if s["type"] == "technical"]
    soft = [s for s in skills if s["type"] == "soft"]
    cats = {s["category"] for s in tech}
    words = re.findall(r"[A-Za-z']+", text.lower())
    verbs = {w for w in words if w in ACTION_VERBS}
    quantified = len(QUANT_RE.findall(text))
    weak = [p for p in WEAK_PHRASES if p in text.lower()]
    first_person = len(re.findall(r"\b(?:i|my|me)\b", text, re.I))
    bullets = text.count("\u2022")
    strengths, issues = [], []
    bd = {}

    # 1. Contact information (10)
    c = (3 if contact.get("name") else 0) + (3 if contact.get("email") else 0) + (2 if contact.get("phone") else 0) \
        + (2 if (contact.get("linkedin") or contact.get("github")) else 0)
    bd["Contact Info"] = {"score": _pts(c, 10), "max": 10}
    if not contact.get("email"): issues.append("No email address detected - ATS systems and recruiters need one.")
    if not contact.get("phone"): issues.append("No phone number detected.")
    if not (contact.get("linkedin") or contact.get("github")):
        issues.append("Add a LinkedIn or GitHub profile link to strengthen credibility.")
    if c >= 8: strengths.append("Complete contact information.")

    # 2. Sections (15)
    weights = {"education": 4, "experience": 4, "skills": 3, "projects": 2, "summary": 1, "certifications": 1}
    s = sum(w for k, w in weights.items() if k in sections)
    bd["Sections"] = {"score": _pts(s, 15), "max": 15}
    for k in ("education", "experience", "skills"):
        if k not in sections:
            issues.append(f"Missing a clearly labelled '{k.title()}' section.")
    if "summary" not in sections: issues.append("Add a 2-3 line professional summary at the top.")
    if "projects" not in sections: issues.append("Add a Projects section to showcase practical work.")
    if s >= 12: strengths.append("Well-structured resume with standard section headings.")

    # 3. Skills (20)
    sk = min(len(tech), 12) / 12 * 14 + min(len(soft), 4) / 4 * 3 + min(len(cats), 4) / 4 * 3
    bd["Skills"] = {"score": _pts(sk, 20), "max": 20}
    if len(tech) < 6: issues.append(f"Only {len(tech)} technical skills detected - list more relevant tools and technologies.")
    elif len(tech) >= 10: strengths.append(f"Strong technical skill set ({len(tech)} skills detected).")
    if not soft: issues.append("No soft skills (communication, teamwork, leadership) detected.")

    # 4. Experience & projects (20)
    exp_pts = (min(parsed["experience_years"], 5) / 5 * 10 + min(counts["experience"], 3) / 3 * 4
               + min(quantified, 5) / 5 * 3 + min(len(verbs), 8) / 8 * 3)
    proj_pts = min(counts["projects"], 3) / 3 * 12 + min(quantified, 5) / 5 * 4 + min(len(verbs), 8) / 8 * 4
    ex = max(exp_pts, proj_pts * 0.9)
    bd["Experience"] = {"score": _pts(ex, 20), "max": 20}
    if counts["experience"] == 0 and counts["projects"] == 0:
        issues.append("No work experience or projects detected - add internships, projects or freelance work.")
    elif parsed["experience_years"] >= 2: strengths.append(f"About {parsed['experience_years']} years of experience detected.")
    if counts["projects"] >= 2: strengths.append(f"{counts['projects']} projects listed.")

    # 5. Education (10)
    ed = (6 if counts["education"] else 0) + (2 if any(e.get("degree") for e in parsed["education"]) else 0) \
        + (2 if any(e.get("year") or e.get("grade") for e in parsed["education"]) else 0)
    bd["Education"] = {"score": _pts(ed, 10), "max": 10}
    if not counts["education"]: issues.append("Education details were not detected.")

    # 6. Content quality / keywords (15)
    q = min(len(verbs), 10) / 10 * 6 + min(quantified, 6) / 6 * 5 + (2 if first_person == 0 else 0) + (2 if not weak else 0)
    bd["Content Quality"] = {"score": _pts(q, 15), "max": 15}
    if len(verbs) < 5: issues.append("Start bullet points with strong action verbs (built, designed, optimized...).")
    if quantified < 3: issues.append("Quantify achievements with numbers (e.g. 'reduced load time by 35%').")
    else: strengths.append("Achievements include measurable results.")
    if weak: issues.append("Replace weak phrases (" + ", ".join(weak[:3]) + ") with impact-driven statements.")
    if first_person > 2: issues.append("Avoid first-person pronouns (I, my, me) in a resume.")

    # 7. Formatting (10)
    wc = meta.get("word_count", len(words))
    f = 0.0
    f += 4 if 300 <= wc <= 900 else (2 if 150 <= wc < 300 or 900 < wc <= 1200 else 0)
    f += 2 if meta.get("pages", 1) <= 2 else 0
    f += 2 if len(sections - {"other"}) >= 3 else 0
    f += 1 if meta.get("tables", 0) == 0 and meta.get("images", 0) <= 1 else 0
    f += 1 if bullets >= 5 else 0
    bd["Formatting"] = {"score": _pts(f, 10), "max": 10}
    if wc < 300: issues.append(f"Resume is short ({wc} words); aim for 400-800 words.")
    if wc > 1200 or meta.get("pages", 1) > 2: issues.append("Resume is too long - keep it to 1-2 pages.")
    if meta.get("tables", 0) or meta.get("images", 0) > 1:
        issues.append("Tables/images can confuse ATS parsers - prefer a simple single-column layout.")
    if bullets < 5: issues.append("Use bullet points to make accomplishments scannable.")

    total = round(sum(v["score"] for v in bd.values()))
    return {"score": max(0, min(100, total)), "breakdown": bd, "strengths": strengths, "issues": issues,
            "metrics": {"word_count": wc, "pages": meta.get("pages", 1), "action_verbs": len(verbs),
                        "quantified_achievements": quantified, "technical_skills": len(tech),
                        "soft_skills": len(soft), "skill_categories": len(cats)}}


def grade(score: float) -> str:
    return "Excellent" if score >= 80 else "Good" if score >= 65 else "Fair" if score >= 50 else "Needs work"
