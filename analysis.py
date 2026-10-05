import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..ai.skill_extractor import extract_skills
from ..ai.text_extractor import ExtractionError, extract_text
from ..database import get_db
from ..deps import get_current_user
from ..models import AnalysisHistory, AnalysisResult, JobDescription, Resume, User
from ..schemas import AnalysisRequest, SkillExtractRequest
from ..services import analysis_service as asvc
from ..services.report_service import build_report

router = APIRouter(prefix="/api", tags=["Analysis"])


def _own_analysis(db: Session, user: User, analysis_id: int) -> AnalysisResult:
    a = db.get(AnalysisResult, analysis_id)
    if not a or a.resume.user_id != user.id:
        raise HTTPException(404, "Analysis not found")
    return a


@router.post("/analysis/match", status_code=201)
def match_job(body: AnalysisRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Compare a resume with a job description (semantic + skill + keyword similarity)."""
    resume = db.get(Resume, body.resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    analysis = asvc.run_analysis(db, user, resume, body.job_description.strip(), body.job_title)
    return asvc.serialize_analysis(analysis)


@router.get("/analysis")
def list_analyses(resume_id: int | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(AnalysisResult).join(Resume).filter(Resume.user_id == user.id)
    if resume_id:
        q = q.filter(AnalysisResult.resume_id == resume_id)
    return [asvc.serialize_analysis(a, full=False) for a in q.order_by(AnalysisResult.created_at.desc()).all()]


@router.post("/analysis/resume/{resume_id}", status_code=201)
def reanalyze(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(404, "Resume not found")
    return asvc.serialize_analysis(asvc.run_analysis(db, user, resume))


@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return asvc.serialize_analysis(_own_analysis(db, user, analysis_id))


@router.delete("/analysis/{analysis_id}")
def delete_analysis(analysis_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _own_analysis(db, user, analysis_id)
    asvc.log_history(db, user.id, "analysis_delete", f"Analysis #{a.id} of {a.resume.filename}")
    db.delete(a)
    db.commit()
    return {"message": "Analysis deleted"}


@router.get("/analysis/{analysis_id}/report")
def download_report(analysis_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = _own_analysis(db, user, analysis_id)
    pdf = build_report(asvc.serialize_analysis(a), user.full_name)
    asvc.log_history(db, user.id, "report_download", f"Report for analysis #{a.id}", a.resume_id, a.id)
    db.commit()
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="analysis_report_{a.id}.pdf"'})


@router.get("/history")
def activity_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(AnalysisHistory).filter(AnalysisHistory.user_id == user.id)
            .order_by(AnalysisHistory.created_at.desc()).limit(100).all())
    return [{"id": h.id, "action": h.action, "details": h.details, "resume_id": h.resume_id,
             "analysis_id": h.analysis_id, "created_at": h.created_at} for h in rows]


@router.post("/skills/extract", tags=["Skills"])
def skills_extract(body: SkillExtractRequest, _: User = Depends(get_current_user)):
    return {"skills": extract_skills(body.text)}


@router.post("/jobs/extract-text", tags=["Jobs"])
async def jd_extract_text(file: UploadFile = File(...), _: User = Depends(get_current_user)):
    """Read a job description from an uploaded PDF/DOCX/TXT file."""
    name = (file.filename or "").lower()
    ext = name.rsplit(".", 1)[-1] if "." in name else ""
    content = await file.read()
    if len(content) > 3 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 3 MB)")
    if ext == "txt":
        return {"text": content.decode("utf-8", errors="ignore")[:30000]}
    if ext not in ("pdf", "docx"):
        raise HTTPException(415, "Upload a PDF, DOCX or TXT file")
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(content)
        path = tmp.name
    try:
        text, _meta = extract_text(path, ext)
    except ExtractionError as exc:
        raise HTTPException(422, str(exc))
    finally:
        os.remove(path)
    return {"text": text[:30000]}


@router.get("/jobs", tags=["Jobs"])
def list_jobs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(JobDescription).filter(JobDescription.user_id == user.id).order_by(JobDescription.created_at.desc()).limit(50).all()
    return [{"id": j.id, "title": j.title, "content": j.content, "skills": j.extracted_skills,
             "created_at": j.created_at} for j in rows]
