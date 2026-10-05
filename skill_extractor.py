"""Dictionary + alias based skill extraction using boundary-aware regex matching."""
import re

from .skills_db import ALIASES, CASE_SENSITIVE, SKILL_CATEGORIES, SKILL_TO_CATEGORY, SOFT_SKILLS

_LB = r"(?<![\w+#.\-])"
_LA = r"(?![\w+#]|\.\w)"


def _build(terms: dict[str, str], flags: int):
    if not terms:
        return None
    keys = sorted(terms, key=len, reverse=True)
    pattern = _LB + "(" + "|".join(re.escape(k) for k in keys) + ")" + _LA
    return re.compile(pattern, flags)


_ci, _cs = {}, {}
for _skill in SKILL_TO_CATEGORY:
    (_cs if _skill in CASE_SENSITIVE else _ci)[_skill.lower() if _skill not in CASE_SENSITIVE else _skill] = _skill
for _alias, _skill in ALIASES.items():
    if _skill in CASE_SENSITIVE:
        continue
    _ci[_alias.lower()] = _skill
_CI_RE = _build(_ci, re.IGNORECASE)
_CS_RE = _build(_cs, 0)


def extract_skills(text: str) -> list[dict]:
    """Return unique skills found in text as [{'name', 'category', 'type'}] sorted by category then name."""
    found: dict[str, int] = {}
    for m in _CI_RE.finditer(text):
        found.setdefault(_ci[m.group(1).lower()], m.start())
    for m in _CS_RE.finditer(text):
        found.setdefault(_cs[m.group(1)], m.start())
    skills = [{"name": n, "category": SKILL_TO_CATEGORY[n],
               "type": "soft" if n in SOFT_SKILLS else "technical"} for n in found]
    order = list(SKILL_CATEGORIES)
    skills.sort(key=lambda s: (order.index(s["category"]), s["name"].lower()))
    return skills


def skill_names(text: str) -> list[str]:
    return [s["name"] for s in extract_skills(text)]
