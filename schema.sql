-- PostgreSQL schema for the AI Resume Analyzer.
-- The backend creates these tables automatically on startup (SQLAlchemy create_all);
-- this file is provided for documentation, pgAdmin imports, or manual setup:
--   psql -U postgres -d resume_analyzer -f database/schema.sql

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

CREATE TABLE IF NOT EXISTS resumes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  stored_name VARCHAR(255) NOT NULL,
  file_type VARCHAR(10) NOT NULL,
  file_size INTEGER DEFAULT 0,
  raw_text TEXT NOT NULL,
  full_name VARCHAR(120), email VARCHAR(255), phone VARCHAR(50),
  linkedin VARCHAR(255), github VARCHAR(255), summary TEXT,
  total_experience_years DOUBLE PRECISION DEFAULT 0,
  parsed_data JSON, meta JSON,
  uploaded_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes(user_id);

CREATE TABLE IF NOT EXISTS skills (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  category VARCHAR(60)
);

CREATE TABLE IF NOT EXISTS resume_skills (
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (resume_id, skill_id)
);

CREATE TABLE IF NOT EXISTS education (
  id SERIAL PRIMARY KEY,
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  degree VARCHAR(255), institution VARCHAR(255), year VARCHAR(50), grade VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS ix_education_resume_id ON education(resume_id);

CREATE TABLE IF NOT EXISTS experience (
  id SERIAL PRIMARY KEY,
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  title VARCHAR(255), company VARCHAR(255), duration VARCHAR(100), description TEXT
);
CREATE INDEX IF NOT EXISTS ix_experience_resume_id ON experience(resume_id);

CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  name VARCHAR(255), description TEXT, technologies JSON
);
CREATE INDEX IF NOT EXISTS ix_projects_resume_id ON projects(resume_id);

CREATE TABLE IF NOT EXISTS certifications (
  id SERIAL PRIMARY KEY,
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  name VARCHAR(255)
);
CREATE INDEX IF NOT EXISTS ix_certifications_resume_id ON certifications(resume_id);

CREATE TABLE IF NOT EXISTS job_descriptions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255), content TEXT NOT NULL, extracted_skills JSON,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_job_descriptions_user_id ON job_descriptions(user_id);

CREATE TABLE IF NOT EXISTS analysis_results (
  id SERIAL PRIMARY KEY,
  resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  job_description_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL,
  ats_score DOUBLE PRECISION NOT NULL,
  ats_breakdown JSON, strengths JSON, issues JSON,
  job_match_score DOUBLE PRECISION, skill_match_score DOUBLE PRECISION,
  semantic_score DOUBLE PRECISION, keyword_score DOUBLE PRECISION,
  similarity_method VARCHAR(50),
  matched_skills JSON, missing_skills JSON, missing_keywords JSON,
  suggested_roles JSON, skill_gaps JSON, learning_path JSON,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_analysis_results_resume_id ON analysis_results(resume_id);
CREATE INDEX IF NOT EXISTS ix_analysis_results_created_at ON analysis_results(created_at);

CREATE TABLE IF NOT EXISTS recommendations (
  id SERIAL PRIMARY KEY,
  analysis_id INTEGER NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
  category VARCHAR(60), priority VARCHAR(10), text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_recommendations_analysis_id ON recommendations(analysis_id);

CREATE TABLE IF NOT EXISTS analysis_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
  analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE SET NULL,
  action VARCHAR(50) NOT NULL, details VARCHAR(500),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_analysis_history_user_id ON analysis_history(user_id);
CREATE INDEX IF NOT EXISTS ix_analysis_history_created_at ON analysis_history(created_at);
