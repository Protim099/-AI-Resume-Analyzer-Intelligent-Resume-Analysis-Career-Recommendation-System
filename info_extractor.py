"""Information extraction: contact info, education, experience, projects, certifications."""
import re
from datetime import date

from .preprocessing import BULLET_RE, get_nlp, has_ner
from .skill_extractor import skill_names

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s().\-]{8,17}\d)(?!\d)")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[A-Za-z0-9_\-/%]+", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_\-]+", re.I)

SECTION_HEADERS = {
    "summary": ["summary", "professional summary", "objective", "career objective", "profile", "about me", "about"],
    "education": ["education", "academic background", "academic qualifications", "education and training",
                  "educational qualifications", "academics"],
    "experience": ["experience", "work experience", "professional experience", "employment history",
                   "work history", "internships", "internship experience", "employment", "career history"],
    "projects": ["projects", "academic projects", "personal projects", "key projects", "project experience",
                 "selected projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "key skills",
               "skills and tools", "technical proficiency", "skills summary"],
    "certifications": ["certifications", "certificates", "licenses", "licenses and certifications",
                       "courses", "training", "certifications and courses", "courses and certifications"],
    "other": ["achievements", "awards", "honors", "publications", "languages", "interests", "hobbies",
              "references", "activities", "extracurricular activities", "volunteering", "leadership",
              "declaration", "personal details", "personal information", "co-curricular activities"],
}
HEADER_LOOKUP = {h: sec for sec, hs in SECTION_HEADERS.items() for h in hs}

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
DATE_TOKEN = rf"(?:(?:{MONTHS})[a-z]*\.?,?\s+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
PRESENT = r"(?:present|current|now|ongoing|till date|to date)"
DATE_RANGE_RE = re.compile(rf"({DATE_TOKEN})\s*(?:-|\u2013|\u2014|to)\s*({DATE_TOKEN}|{PRESENT})", re.I)
DEGREE_RE = re.compile(
    r"\b(B\.?\s?Sc\.?|B\.?\s?Tech\.?|B\.?\s?E\.?|B\.?\s?S\.?|B\.?\s?A\.?|BBA|BCA|Bachelor[^,\n|]*|M\.?\s?Sc\.?|"
    r"M\.?\s?Tech\.?|M\.?\s?E\.?|MBA|MCA|M\.?\s?S\.?|Master[^,\n|]*|Ph\.?\s?D\.?|Doctorate|Diploma[^,\n|]*|"
    r"HSC|SSC|A[- ]Levels?|O[- ]Levels?|Higher Secondary[^,\n|]*|Secondary School[^,\n|]*|Associate[^,\n|]*)\b", re.I)
INSTITUTION_RE = re.compile(r"\b(University|College|Institute|School|Academy|Polytechnic|IIT|NIT|BUET)\b", re.I)
GRADE_RE = re.compile(r"\b(?:CGPA|GPA|Grade|Percentage|Score)\s*[:\-]?\s*([\d.]+(?:\s*/\s*[\d.]+)?%?)", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b(?:\s*(?:-|\u2013|\u2014|to)\s*(?:\b(?:19|20)\d{2}\b|present|current|expected)?)?", re.I)
CERT_HINT_RE = re.compile(r"\b(certified|certification|certificate|nanodegree|specialization|credential)\b", re.I)


def _norm_header(line: str) -> str:
    return re.sub(r"[^a-z& ]", "", line.lower()).replace("&", "and").strip()


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"header": []}
    current = "header"
    for line in text.split("\n"):
        stripped = line.strip()
        norm = _norm_header(stripped)
        is_header = (norm in HEADER_LOOKUP and len(stripped.split()) <= 5 and not stripped.startswith("\u2022")
                     and len(stripped) < 45)
        if is_header:
            current = HEADER_LOOKUP[norm]
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(stripped)
    return {k: [l for l in v if l] for k, v in sections.items()}


# ---------------------------------------------------------------- contact
def extract_contact(text: str) -> dict:
    email = EMAIL_RE.search(text)
    phone = None
    head = "\n".join(text.split("\n")[:25])
    for m in PHONE_RE.finditer(head + "\n" + text):
        digits = re.sub(r"\D", "", m.group(1))
        if 10 <= len(digits) <= 15 and not re.fullmatch(r"(?:(?:19|20)\d{2}\D*){2,}", m.group(1).strip()):
            phone = re.sub(r"\s+", " ", m.group(1)).strip()
            break
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)
    return {"name": extract_name(text, email.group(0) if email else None),
            "email": email.group(0) if email else None, "phone": phone,
            "linkedin": linkedin.group(0) if linkedin else None,
            "github": github.group(0) if github else None}


def extract_name(text: str, email: str | None) -> str | None:
    lines = [l.strip() for l in text.split("\n") if l.strip()][:10]
    for line in lines:
        if "@" in line or any(c.isdigit() for c in line) or _norm_header(line) in HEADER_LOOKUP:
            continue
        clean = re.sub(r"[^A-Za-z.\' \-]", "", line).strip()
        words = clean.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() or w.isupper() for w in words if w[0].isalpha()):
            return clean.title() if clean.isupper() else clean
    if has_ner():
        doc = get_nlp()(" ".join(lines)[:400])
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                return ent.text.strip()
    if email:
        local = re.sub(r"[\d_]+", " ", email.split("@")[0]).replace(".", " ").strip()
        return local.title() or None
    return None


# ---------------------------------------------------------------- education
def extract_education(sections: dict, text: str) -> list[dict]:
    lines = sections.get("education") or [l for l in text.split("\n") if DEGREE_RE.search(l) or INSTITUTION_RE.search(l)][:8]
    entries: list[dict] = []
    cur: dict = {}

    def push():
        nonlocal cur
        if cur.get("degree") or cur.get("institution"):
            entries.append(cur)
        cur = {}

    for line in lines:
        line = BULLET_RE.sub("", line).strip()
        deg, inst = DEGREE_RE.search(line), INSTITUTION_RE.search(line)
        if deg and cur.get("degree"):
            push()
        if inst and cur.get("institution") and (cur.get("degree") or deg):
            push()
        if deg and not cur.get("degree"):
            parts = [x.strip() for x in re.split(r"\s*[|,\u2013\u2014]\s*|\s+-\s+", line) if x.strip()]
            cur["degree"] = next((x for x in parts if DEGREE_RE.search(x)), line)[:200]
        if inst and not cur.get("institution"):
            part = next((p.strip() for p in re.split(r"\s*[|,\u2013\u2014]\s*|\s+-\s+", line) if INSTITUTION_RE.search(p)), line)
            cur["institution"] = part[:200]
        y = YEAR_RE.search(line)
        if y and not cur.get("year"):
            cur["year"] = y.group(0).strip()
        g = GRADE_RE.search(line)
        if g and not cur.get("grade"):
            cur["grade"] = g.group(1)
    push()
    return entries[:6]


# ---------------------------------------------------------------- experience
def _parse_date(token: str) -> tuple[int, int]:
    token = token.strip().lower()
    today = date.today()
    if re.fullmatch(PRESENT, token):
        return today.year, today.month
    m = re.match(rf"({MONTHS})[a-z]*\.?,?\s+(\d{{4}})", token)
    if m:
        months = "jan feb mar apr may jun jul aug sep oct nov dec".split()
        return int(m.group(2)), months.index(m.group(1)[:3]) + 1
    m = re.match(r"(\d{1,2})/(\d{4})", token)
    if m:
        return int(m.group(2)), min(max(int(m.group(1)), 1), 12)
    return int(token[:4]), 1


def _months(rng: tuple[str, str]) -> tuple[int, int]:
    (y1, m1), (y2, m2) = _parse_date(rng[0]), _parse_date(rng[1])
    return y1 * 12 + m1, y2 * 12 + m2


def total_years(ranges: list[tuple[str, str]]) -> float:
    spans = []
    for r in ranges:
        try:
            a, b = _months(r)
            if b >= a:
                spans.append((a, b))
        except (ValueError, IndexError):
            continue
    spans.sort()
    merged: list[list[int]] = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return round(sum(b - a for a, b in merged) / 12, 1)


def _split_title_company(header: str) -> tuple[str, str]:
    header = BULLET_RE.sub("", header).strip(" |,-\u2013\u2014")
    parts = [p.strip() for p in re.split(r"\s+(?:at|@)\s+|\s*[|,\u2013\u2014]\s*|\s+-\s+", header) if p.strip()]
    return (parts[0] if parts else "")[:200], (parts[1] if len(parts) > 1 else "")[:200]


def _is_bullet(line: str) -> bool:
    return line.startswith("\u2022")


def extract_experience(sections: dict) -> tuple[list[dict], float]:
    lines = sections.get("experience", [])
    anchors = [i for i, l in enumerate(lines) if DATE_RANGE_RE.search(l) and not _is_bullet(l)]
    entries, ranges = [], []
    if anchors:
        starts = []
        for i in anchors:
            prev = lines[i - 1] if i > 0 else ""
            line_wo_date = DATE_RANGE_RE.sub("", lines[i]).strip(" |,-\u2013\u2014()")
            use_prev = bool(prev) and not _is_bullet(prev) and len(prev) < 90 and (i - 1) not in anchors and len(line_wo_date) < 60
            starts.append(i - 1 if use_prev and (not starts or i - 1 > anchors[anchors.index(i) - 1] + 0) else i)
        for n, i in enumerate(anchors):
            m = DATE_RANGE_RE.search(lines[i])
            ranges.append((m.group(1), m.group(2)))
            head_lines = [DATE_RANGE_RE.sub("", lines[i]).strip(" |,-\u2013\u2014()")]
            if starts[n] != i:
                head_lines.insert(0, lines[starts[n]])
            end = starts[n + 1] if n + 1 < len(anchors) else len(lines)
            title, company = _split_title_company(" | ".join(h for h in head_lines if h))
            desc = [BULLET_RE.sub("", l) for l in lines[i + 1:end]]
            entries.append({"title": title, "company": company, "duration": f"{m.group(1)} - {m.group(2)}",
                            "description": "\n".join(desc).strip()})
    else:
        cur = None
        for l in lines:
            if not _is_bullet(l) and len(l) < 90:
                if cur:
                    entries.append(cur)
                t, c = _split_title_company(l)
                cur = {"title": t, "company": c, "duration": "", "description": ""}
            elif cur:
                cur["description"] += BULLET_RE.sub("", l) + "\n"
        if cur:
            entries.append(cur)
    for e in entries:
        e["description"] = e["description"].strip()
    return entries[:10], total_years(ranges)


# ---------------------------------------------------------------- projects
def extract_projects(sections: dict) -> list[dict]:
    lines = sections.get("projects", [])
    projects, cur = [], None
    for l in lines:
        if not _is_bullet(l) and len(l) < 100 and not re.match(r"^(tech|technologies|tools|stack)\b", l, re.I):
            if cur:
                projects.append(cur)
            cur = {"name": re.split(r"\s*[|\u2013\u2014]\s*|\s+-\s+|:", l)[0].strip()[:200], "description": ""}
        elif cur is not None:
            cur["description"] += BULLET_RE.sub("", l) + "\n"
        else:
            cur = {"name": "Project", "description": BULLET_RE.sub("", l) + "\n"}
    if cur:
        projects.append(cur)
    for p in projects:
        p["description"] = p["description"].strip()
        p["technologies"] = skill_names(p["name"] + " " + p["description"])
    return projects[:8]


# ---------------------------------------------------------------- certifications
def extract_certifications(sections: dict, text: str) -> list[str]:
    lines = sections.get("certifications")
    if not lines:
        lines = [l for l in text.split("\n") if CERT_HINT_RE.search(l) and len(l) < 150]
    certs, seen = [], set()
    for l in lines:
        c = BULLET_RE.sub("", l).strip()
        if 3 <= len(c) <= 200 and c.lower() not in seen:
            seen.add(c.lower())
            certs.append(c)
    return certs[:10]
