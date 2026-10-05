from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AnalysisResult, Resume, User
from ..services import analysis_service as asvc
from ..services import resume_service as rsvc

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


def _own(db: Session, user: User, resume_id: int) -> Resume:
    r = db.get(Resume, resume_id)
    if not r or r.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    return r


@router.post("/upload", status_code=201)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    """Upload -> extract text -> NLP parse -> store entities -> run ATS analysis."""
    resume = await rsvc.create_resume(db, user, file)
    asvc.log_history(db, user.id, "resume_upload", resume.filename, resume.id)
    db.commit()
    analysis = asvc.run_analysis(db, user, resume)
    return {"resume": rsvc.serialize_resume(resume, analysis.ats_score), "analysis_id": analysis.id}


@router.get("")
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.uploaded_at.desc()).all()
    out = []
    for r in rows:
        latest = (db.query(AnalysisResult.ats_score).filter(AnalysisResult.resume_id == r.id)
                  .order_by(AnalysisResult.created_at.desc()).first())
        out.append(rsvc.serialize_resume(r, latest[0] if latest else None))
    return out


@router.get("/{resume_id}")
def get_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = _own(db, user, resume_id)
    data = rsvc.serialize_resume(r)
    data.update({"parsed": r.parsed_data, "text_preview": r.raw_text[:3000],
                 "analysis_count": db.query(func.count(AnalysisResult.id)).filter(AnalysisResult.resume_id == r.id).scalar()})
    return data


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = _own(db, user, resume_id)
    rsvc.delete_resume_file(r)
    asvc.log_history(db, user.id, "resume_delete", r.filename)
    db.delete(r)
    db.commit()
    return {"message": "Resume deleted"}
