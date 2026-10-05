# API Documentation

Base URL: `http://localhost:8000/api` - interactive Swagger UI at **http://localhost:8000/docs**, ReDoc at `/redoc`.
All endpoints except register, login and health require the header `Authorization: Bearer <JWT>`.
Errors are returned as `{"detail": "message"}` with a suitable HTTP status (400, 401, 403, 404, 409, 413, 415, 422).

## Authentication
| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `/auth/register` | `{full_name, email, password}` | Create account, returns `{access_token, user}`. Password: 8+ chars with a letter and a number |
| POST | `/auth/login` | `{email, password}` | Returns `{access_token, token_type, user}` |
| POST | `/auth/logout` | - | Stateless logout acknowledgement (client deletes the token) |
| GET | `/auth/me` | - | Current user |
| PUT | `/users/me` | `{full_name}` | Update profile |
| PUT | `/users/me/password` | `{current_password, new_password}` | Change password |

## Resumes
| Method | Endpoint | Description |
|---|---|---|
| POST | `/resumes/upload` | `multipart/form-data` field `file` (PDF/DOCX, max 5 MB). Runs the whole pipeline and returns `{resume, analysis_id}` |
| GET | `/resumes` | List your resumes with latest ATS score |
| GET | `/resumes/{id}` | Parsed data (contact, education, experience, projects, skills) and a text preview |
| DELETE | `/resumes/{id}` | Delete resume, file and all of its analyses |

## Analysis, matching and reports
| Method | Endpoint | Body | Description |
|---|---|---|---|
| POST | `/analysis/match` | `{resume_id, job_title?, job_description}` | Job match: score, skill/semantic/keyword scores, matched and missing skills, keywords, roles, gaps |
| POST | `/analysis/resume/{resume_id}` | - | Re-run the ATS analysis |
| GET | `/analysis` | query `resume_id?` | List analyses (history) |
| GET | `/analysis/{id}` | - | Full result: ATS breakdown, strengths, issues, recommendations, extracted info, roles, gaps, learning path |
| DELETE | `/analysis/{id}` | - | Delete an analysis |
| GET | `/analysis/{id}/report` | - | Download a PDF report |
| GET | `/history` | - | Activity log (uploads, analyses, downloads) |
| POST | `/skills/extract` | `{text}` | Extract technical and soft skills from any text |
| POST | `/jobs/extract-text` | file (PDF/DOCX/TXT) | Read a job description from a file |
| GET | `/jobs` | - | Your saved job descriptions |
| GET | `/dashboard/stats` | - | Dashboard numbers, ATS trend, top skills |

## Admin (role `admin` only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/stats` | Totals, average ATS/match, popular skills, ATS distribution, sign-ups |
| GET | `/admin/users` | All users with resume and analysis counts |
| PATCH | `/admin/users/{id}` | `{role?: "user"|"admin", is_active?: bool}` |
| DELETE | `/admin/users/{id}` | Delete a user and all of their data |
| GET | `/admin/resumes` | Latest resumes |

## System
`GET /api/health` returns `{"status": "ok"}`.

## Example
```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"Admin@12345"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -X POST localhost:8000/api/resumes/upload -H "Authorization: Bearer $TOKEN" -F file=@resume.pdf
```
