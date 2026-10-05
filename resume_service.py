import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..ai import pipeline
from ..ai.text_extractor import ExtractionError
from ..config import settings
from ..models import (Certification, Education, Experience, Project, Resume, ResumeSkill, Skill, User)

ALLOWED = {"pdf": [b"%PDF"], "docx": [b"PK\x03\x04"]}


def _upload_dir() -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    return settings.UPLOAD_DIR


async def save_upload(file: UploadFile) -> tuple[str, str, str, int]:
    """Validate (extension, size, magic bytes) and write file to disk. Returns (path, stored_name, ext, size)."""
    name = file.filename or "resume"
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED:
        raise HTTPException(415, "Only PDF and DOCX files are supported.")
    content = await file.read()
    if not content:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File is too large (max {settings.MAX_UPLOAD_MB} MB).")
    if not any(content.startswith(sig) for sig in ALLOWED[ext]):
        raise HTTPException(400, f"File content does not look like a valid {ext.upper()} document.")
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(_upload_dir(), stored)
    with open(path, "wb") as fh:
        fh.write(content)
    return path, stored, ext, len(content)


def get_or_create_skill(db: Session, name: str, category: str, cache: dict) -> Skill:
    if name in cache:
        return cache[name]
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        skill = Skill(name=name, category=category)
        db.add(skill)
        db.flush()
    cache[name] = skill
    return skill


async def create_resume(db: Session, user: User, file: UploadFile) -> Resume:
    path, stored, ext, size = await save_upload(file)
    try:
        text, meta, parsed = pipeline.parse_resume(path, ext)
    except ExtractionError as exc:
        os.remove(path)
        raise HTTPException(422, str(exc))
    if len(text) < 80:
        os.remove(path)
        raise HTTPException(422, "Could not read text from this file. Scanned/image-only PDFs are not supported - "
                                 "upload a text-based PDF or DOCX.")
    c = parsed["contact"]
    resume = Resume(user_id=user.id, filename=file.filename[:255], stored_name=stored, file_type=ext, file_size=size,
                    raw_text=text, full_name=c.get("name"), email=c.get("email"), phone=c.get("phone"),
                    linkedin=c.get("linkedin"), github=c.get("github"), summary=parsed["summary"],
                    total_experience_years=parsed["experience_years"], parsed_data=parsed, meta=meta)
    db.add(resume)
    db.flush()
    for e in parsed["education"]:
        db.add(Education(resume_id=resume.id, degree=e.get("degree"), institution=e.get("institution"),
                         year=e.get("year"), grade=e.get("grade")))
    for e in parsed["experience"]:
        db.add(Experience(resume_id=resume.id, title=e["title"], company=e["company"],
                          duration=e["duration"], description=e["description"]))
    for p in parsed["projects"]:
        db.add(Project(resume_id=resume.id, name=p["name"], description=p["description"],
                       technologies=p["technologies"]))
    for name in parsed["certifications"]:
        db.add(Certification(resume_id=resume.id, name=name))
    cache: dict = {}
    for s in parsed["skills"]:
        skill = get_or_create_skill(db, s["name"], s["category"], cache)
        db.add(ResumeSkill(resume_id=resume.id, skill_id=skill.id))
    db.commit()
    db.refresh(resume)
    return resume


def delete_resume_file(resume: Resume) -> None:
    try:
        os.remove(os.path.join(settings.UPLOAD_DIR, resume.stored_name))
    except OSError:
        pass


def serialize_resume(r: Resume, latest_ats: float | None = None) -> dict:
    return {"id": r.id, "filename": r.filename, "file_type": r.file_type, "file_size": r.file_size,
            "full_name": r.full_name, "email": r.email, "phone": r.phone,
            "total_experience_years": r.total_experience_years,
            "skills_count": (r.parsed_data or {}).get("counts", {}).get("skills", 0),
            "latest_ats_score": latest_ats, "uploaded_at": r.uploaded_at}
