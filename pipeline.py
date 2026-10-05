"""End-to-end AI pipeline:
Upload -> text extraction -> NLP preprocessing -> information extraction -> skill extraction
-> ATS scoring -> JD matching -> skill-gap detection -> career recommendations."""
from . import ats_scorer, info_extractor as ie, matcher, recommender
from .preprocessing import clean_text
from .skill_extractor import extract_skills
from .text_extractor import extract_text


def parse_resume(path: str, file_type: str) -> tuple[str, dict, dict]:
    raw, meta = extract_text(path, file_type)
    text = clean_text(raw)
    sections = ie.split_sections(text)
    contact = ie.extract_contact(text)
    education = ie.extract_education(sections, text)
    experience, years = ie.extract_experience(sections)
    projects = ie.extract_projects(sections)
    certs = ie.extract_certifications(sections, text)
    skills = extract_skills(text)
    summary = " ".join(sections.get("summary", []))[:600] or None
    parsed = {
        "contact": contact, "summary": summary, "education": education, "experience": experience,
        "projects": projects, "certifications": certs, "skills": skills, "experience_years": years,
        "sections_found": [k for k, v in sections.items() if k != "header" and v],
        "counts": {"education": len(education), "experience": len(experience), "projects": len(projects),
                   "certifications": len(certs), "skills": len(skills)},
    }
    return text, meta, parsed


def analyze(text: str, meta: dict, parsed: dict, jd_text: str | None = None) -> dict:
    ats = ats_scorer.score_resume(parsed, text, meta)
    names = [s["name"] for s in parsed["skills"]]
    match = matcher.match_resume_to_job(text, names, jd_text) if jd_text else None
    roles = recommender.suggest_roles(names)
    gaps = recommender.skill_gaps(roles, match["missing_skills"] if match else None)
    path = recommender.learning_path(names, gaps)
    recs = recommender.build_recommendations(ats, parsed, match, gaps, roles)
    return {"ats": ats, "match": match, "roles": roles, "gaps": gaps, "learning_path": path, "recommendations": recs}
