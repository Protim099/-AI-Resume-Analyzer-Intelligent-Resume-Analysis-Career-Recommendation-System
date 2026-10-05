from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import AnalysisResult, Resume, ResumeSkill, Skill, User
from ..schemas import AdminUserUpdate
from ..services.resume_service import delete_resume_file

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats")
def admin_stats(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(func.count(User.id)).scalar()
    resumes = db.query(func.count(Resume.id)).scalar()
    analyses = db.query(func.count(AnalysisResult.id)).scalar()
    avg_ats = db.query(func.avg(AnalysisResult.ats_score)).scalar()
    avg_match = db.query(func.avg(AnalysisResult.job_match_score)).scalar()
    popular = (db.query(Skill.name, Skill.category, func.count(ResumeSkill.skill_id).label("c"))
               .join(ResumeSkill, ResumeSkill.skill_id == Skill.id).group_by(Skill.id)
               .order_by(func.count(ResumeSkill.skill_id).desc()).limit(10).all())
    buckets = {"0-39": 0, "40-59": 0, "60-79": 0, "80-100": 0}
    for (s,) in db.query(AnalysisResult.ats_score).all():
        buckets["0-39" if s < 40 else "40-59" if s < 60 else "60-79" if s < 80 else "80-100"] += 1
    since = datetime.now(timezone.utc) - timedelta(days=13)
    signups: dict[str, int] = {}
    for (d,) in db.query(User.created_at).filter(User.created_at >= since).all():
        signups[d.date().isoformat()] = signups.get(d.date().isoformat(), 0) + 1
    days = [(since + timedelta(days=i)).date().isoformat() for i in range(14)]
    return {
        "total_users": users, "total_resumes": resumes, "total_analyses": analyses,
        "average_ats": round(avg_ats or 0, 1), "average_match": round(avg_match, 1) if avg_match else None,
        "popular_skills": [{"name": n, "category": c, "count": k} for n, c, k in popular],
        "ats_distribution": [{"range": k, "count": v} for k, v in buckets.items()],
        "signups": [{"date": d, "count": signups.get(d, 0)} for d in days],
    }


@router.get("/users")
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    out = []
    for u in db.query(User).order_by(User.created_at.desc()).all():
        rc = db.query(func.count(Resume.id)).filter(Resume.user_id == u.id).scalar()
        ac = db.query(func.count(AnalysisResult.id)).join(Resume).filter(Resume.user_id == u.id).scalar()
        out.append({"id": u.id, "full_name": u.full_name, "email": u.email, "role": u.role, "is_active": u.is_active,
                    "created_at": u.created_at, "last_login": u.last_login, "resumes": rc, "analyses": ac})
    return out


@router.patch("/users/{user_id}")
def update_user(user_id: int, body: AdminUserUpdate, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if u.id == admin.id and (body.is_active is False or body.role == "user"):
        raise HTTPException(400, "You cannot deactivate or demote your own account")
    if body.role is not None:
        u.role = body.role
    if body.is_active is not None:
        u.is_active = body.is_active
    db.commit()
    return {"message": "User updated"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if u.id == admin.id:
        raise HTTPException(400, "You cannot delete your own account")
    for r in u.resumes:
        delete_resume_file(r)
    db.delete(u)
    db.commit()
    return {"message": "User deleted"}


@router.get("/resumes")
def list_resumes(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.query(Resume, User.full_name).join(User).order_by(Resume.uploaded_at.desc()).limit(100).all()
    return [{"id": r.id, "filename": r.filename, "owner": name, "skills": (r.parsed_data or {}).get("counts", {}).get("skills", 0),
             "uploaded_at": r.uploaded_at} for r, name in rows]
