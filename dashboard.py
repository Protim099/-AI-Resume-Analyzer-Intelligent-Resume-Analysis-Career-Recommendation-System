from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AnalysisResult, Resume, ResumeSkill, Skill, User
from ..services import analysis_service as asvc

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def user_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    base = db.query(AnalysisResult).join(Resume).filter(Resume.user_id == user.id)
    analyses = base.order_by(AnalysisResult.created_at.asc()).all()
    resumes = db.query(func.count(Resume.id)).filter(Resume.user_id == user.id).scalar()
    ats = [a.ats_score for a in analyses]
    matches = [a.job_match_score for a in analyses if a.job_match_score is not None]
    top = (db.query(Skill.name, func.count(ResumeSkill.skill_id)).join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
           .join(Resume, Resume.id == ResumeSkill.resume_id).filter(Resume.user_id == user.id)
           .group_by(Skill.name).order_by(func.count(ResumeSkill.skill_id).desc()).limit(8).all())
    categories = Counter()
    for r in db.query(Resume).filter(Resume.user_id == user.id).all():
        for s in (r.parsed_data or {}).get("skills", []):
            categories[s["category"]] += 1
    return {
        "total_resumes": resumes, "total_analyses": len(analyses),
        "average_ats": round(sum(ats) / len(ats), 1) if ats else 0, "best_ats": max(ats) if ats else 0,
        "latest_ats": ats[-1] if ats else None,
        "average_match": round(sum(matches) / len(matches), 1) if matches else None,
        "job_matches": len(matches),
        "ats_trend": [{"id": a.id, "date": a.created_at, "score": a.ats_score} for a in analyses[-12:]],
        "top_skills": [{"name": n, "count": c} for n, c in top],
        "skill_categories": [{"category": k, "count": v} for k, v in categories.most_common()],
        "recent": [asvc.serialize_analysis(a, full=False) for a in reversed(analyses[-5:])],
    }
