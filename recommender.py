"""Career recommendations: role suggestions, skill gaps, learning path and improvement tips."""
from .skills_db import RELATED, ROLE_PROFILES, SKILL_TO_CATEGORY


def suggest_roles(skills: list[str], top_n: int = 5) -> list[dict]:
    have = set(skills)
    results = []
    for role, p in ROLE_PROFILES.items():
        core, nice = p["core"], p["nice"]
        mc = [s for s in core if s in have]
        mn = [s for s in nice if s in have]
        if not mc:
            continue
        pct = (len(mc) / len(core)) * 75 + (len(mn) / len(nice)) * 25
        results.append({"role": role, "match": round(pct, 1), "matched": mc + mn,
                        "missing": [s for s in core if s not in have], "missing_nice": [s for s in nice if s not in have]})
    results.sort(key=lambda r: r["match"], reverse=True)
    return results[:top_n]


def skill_gaps(roles: list[dict], extra_missing: list[dict] | None = None) -> list[dict]:
    """Aggregate missing skills across target roles (and the job description, when given)."""
    gaps: dict[str, dict] = {}
    for r in roles[:3]:
        for s in r["missing"]:
            g = gaps.setdefault(s, {"skill": s, "category": SKILL_TO_CATEGORY.get(s, "Other"), "roles": [], "priority": "medium"})
            g["roles"].append(r["role"])
    for s in extra_missing or []:
        g = gaps.setdefault(s["name"], {"skill": s["name"], "category": s["category"], "roles": [], "priority": "medium"})
        g["priority"] = "high"
        g["roles"].append("Target job description")
    for g in gaps.values():
        if g["priority"] != "high" and len(g["roles"]) >= 2:
            g["priority"] = "high"
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(gaps.values(), key=lambda g: (order[g["priority"]], -len(g["roles"]), g["skill"]))[:15]


def learning_path(skills: list[str], gaps: list[dict]) -> list[dict]:
    have, out, seen = set(skills), [], set()
    for g in gaps[:8]:
        out.append({"technology": g["skill"], "reason": "Required by " + ", ".join(dict.fromkeys(g["roles"][:2])),
                    "priority": g["priority"]})
        seen.add(g["skill"])
    for s in skills:
        for rel in RELATED.get(s, []):
            if rel not in have and rel not in seen and len(out) < 12:
                out.append({"technology": rel, "reason": f"Natural next step after {s}", "priority": "low"})
                seen.add(rel)
    return out


def build_recommendations(ats: dict, parsed: dict, match: dict | None, gaps: list[dict], roles: list[dict]) -> list[dict]:
    recs = []

    def add(cat, prio, text):
        recs.append({"category": cat, "priority": prio, "text": text})

    for issue in ats["issues"][:8]:
        prio = "high" if any(k in issue.lower() for k in ("missing", "no email", "no work", "education")) else "medium"
        add("Resume Quality", prio, issue)
    m = ats["metrics"]
    if m["quantified_achievements"] < 3:
        add("Impact", "high", "Rewrite at least 3 bullet points with metrics, e.g. 'Built a REST API serving 5k requests/day, cutting latency by 40%'.")
    if not parsed["contact"].get("linkedin"):
        add("Profile", "low", "Add a LinkedIn URL and keep it consistent with your resume.")
    if match:
        if match["missing_skills"]:
            names = ", ".join(s["name"] for s in match["missing_skills"][:6])
            add("Job Match", "high", f"The job description asks for skills not found in your resume: {names}. Add them if you have the experience, otherwise plan to learn them.")
        if match["missing_keywords"]:
            add("Keywords", "medium", "Naturally include these job-description keywords where truthful: " + ", ".join(match["missing_keywords"][:8]) + ".")
        if match["job_match_score"] < 60:
            add("Job Match", "high", "Tailor your summary and top bullet points to mirror the responsibilities listed in this job posting.")
    if roles:
        add("Career Path", "low", f"Your skills best match: {roles[0]['role']} ({roles[0]['match']:.0f}%). Highlight related projects first.")
    if gaps:
        add("Skill Gap", "medium", "Priority skills to learn: " + ", ".join(g["skill"] for g in gaps[:5]) + ".")
    order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: order[r["priority"]])
    return recs
