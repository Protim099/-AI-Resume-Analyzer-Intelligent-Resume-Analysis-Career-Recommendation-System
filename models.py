from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text, func)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, default=0)
    raw_text = Column(Text, nullable=False)
    full_name = Column(String(120))
    email = Column(String(255))
    phone = Column(String(50))
    linkedin = Column(String(255))
    github = Column(String(255))
    summary = Column(Text)
    total_experience_years = Column(Float, default=0)
    parsed_data = Column(JSON)
    meta = Column(JSON)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    analyses = relationship("AnalysisResult", back_populates="resume", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(60))


class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    resume = relationship("Resume", back_populates="skills")
    skill = relationship("Skill")


class Education(Base):
    __tablename__ = "education"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    degree = Column(String(255))
    institution = Column(String(255))
    year = Column(String(50))
    grade = Column(String(50))
    resume = relationship("Resume", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    duration = Column(String(100))
    description = Column(Text)
    resume = relationship("Resume", back_populates="experience")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(255))
    description = Column(Text)
    technologies = Column(JSON)
    resume = relationship("Resume", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(255))
    resume = relationship("Resume", back_populates="certifications")


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    extracted_skills = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="job_descriptions")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    ats_score = Column(Float, nullable=False)
    ats_breakdown = Column(JSON)
    strengths = Column(JSON)
    issues = Column(JSON)
    job_match_score = Column(Float, nullable=True)
    skill_match_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    keyword_score = Column(Float, nullable=True)
    similarity_method = Column(String(50), nullable=True)
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    missing_keywords = Column(JSON)
    suggested_roles = Column(JSON)
    skill_gaps = Column(JSON)
    learning_path = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    resume = relationship("Resume", back_populates="analyses")
    job_description = relationship("JobDescription")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="CASCADE"), index=True, nullable=False)
    category = Column(String(60))
    priority = Column(String(10))
    text = Column(Text, nullable=False)
    analysis = relationship("AnalysisResult", back_populates="recommendations")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(50), nullable=False)
    details = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
