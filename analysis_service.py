from sqlalchemy.orm import Session

from ..ai import pipeline
from ..models import (AnalysisHistory, AnalysisResult, JobDescription, Recommendation, Resume, User)


def log_history(db: Session, user_id: int, action: str, details: str = "", resume_id=None, analysis_id=None):
    db.add(AnalysisHistory(user_id=user_id, resume_id=resume_id, analysis_id=analysis_id,
                           action=action, details=details[:500]))


def run_analysis(db: Session, user: User, resume: Resume, jd_text: str | None = None,
                 jd_title: str | None = None) -> AnalysisResult:
    result = pipeline.analyze(resume.raw_text, resume.meta or {}, resume.parsed_data, jd_text)
    jd = None
    if jd_text:
        from ..ai.skill_extractor import skill_names
        jd = JobDescription(user_id=user.id, title=jd_title or "Untitled job", content=jd_text,
                            extracted_skills=skill_names(jd_text))
        db.add(jd)
        db.flush()
    ats, match = result["ats"], result["match"] or {}
    analysis = AnalysisResult(
        resume_id=resume.id, job_description_id=jd.id if jd else None, ats_score=ats["score"],
        ats_breakdown={"breakdown": ats["breakdown"], "metrics": ats["metrics"]},
        strengths=ats["strengths"], issues=ats["issues"],
        job_match_score=match.get("job_match_score"), skill_match_score=match.get("skill_match_score"),
        semantic_score=match.get("semantic_score"), keyword_score=match.get("keyword_score"),
        similarity_method=match.get("similarity_method"),
        matched_skills=match.get("matched_skills"), missing_skills=match.get("missing_skills"),
        missing_keywords=match.get("missing_keywords"), suggested_roles=result["roles"],
        skill_gaps=result["gaps"], learning_path=result["learning_path"])
    db.add(analysis)
    db.flush()
    for r in result["recommendations"]:
        db.add(Recommendation(analysis_id=analysis.id, category=r["category"], priority=r["priority"], text=r["text"]))
    action = "job_match" if jd else "ats_analysis"
    detail = f"{resume.filename}" + (f" vs '{jd.title}' - match {match.get('job_match_score')}%" if jd else f" - ATS {ats['score']}")
    log_history(db, user.id, action, detail, resume.id, analysis.id)
    db.commit()
    db.refresh(analysis)
    return analysis


def serialize_analysis(a: AnalysisResult, full: bool = True) -> dict:
    base = {
        "id": a.id, "resume_id": a.resume_id, "resume_filename": a.resume.filename if a.resume else None,
        "job_title": a.job_description.title if a.job_description else None,
        "ats_score": a.ats_score, "job_match_score": a.job_match_score, "created_at": a.created_at,
        "has_job_match": a.job_description_id is not None,
    }
    if not full:
        return base
    p = a.resume.parsed_data if a.resume else {}
    base.update({
        "ats_breakdown": (a.ats_breakdown or {}).get("breakdown", {}), "metrics": (a.ats_breakdown or {}).get("metrics", {}),
        "strengths": a.strengths or [], "issues": a.issues or [],
        "skill_match_score": a.skill_match_score, "semantic_score": a.semantic_score,
        "keyword_score": a.keyword_score, "similarity_method": a.similarity_method,
        "matched_skills": a.matched_skills or [], "missing_skills": a.missing_skills or [],
        "missing_keywords": a.missing_keywords or [], "suggested_roles": a.suggested_roles or [],
        "skill_gaps": a.skill_gaps or [], "learning_path": a.learning_path or [],
        "recommendations": [{"category": r.category, "priority": r.priority, "text": r.text} for r in a.recommendations],
        "resume": {"contact": p.get("contact", {}), "summary": p.get("summary"), "skills": p.get("skills", []),
                   "education": p.get("education", []), "experience": p.get("experience", []),
                   "projects": p.get("projects", []), "certifications": p.get("certifications", []),
                   "experience_years": p.get("experience_years", 0)},
    })
    return base
