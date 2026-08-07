#!/usr/bin/env python3
"""One file per role: facts in front matter, prose in sections, JD in the body.

The split is the point. Step 1 writes the facts and Step 2 writes only the prose,
so a model cannot restate when a role was posted. The parser is strict for the
same reason a compiler is: a file that does not match the shape is an error that
stops that one role, not a shape to be inferred.
"""
from __future__ import annotations
import dataclasses, datetime as dt, pathlib, re
import yaml

from jobdiscovery import freshness   # for WINDOW_HOURS only

PROSE_SECTIONS = ("cover_letter", "why_interested", "why_it_fits", "resume_tailoring", "notes")
SECTION_TO_COLUMN = {"cover_letter": "C", "why_interested": "D", "why_it_fits": "N",
                     "resume_tailoring": "O", "notes": "R"}
FACT_FIELDS = ("status", "job_url", "date_found", "company", "role", "location",
               "work_mode", "posted", "freshness_confidence", "requisition_id", "fit_score")
FIELD_TO_COLUMN = {"status": "A", "job_url": "B", "date_found": "E", "company": "F",
                   "role": "G", "location": "H", "work_mode": "I", "posted": "J",
                   "freshness_confidence": "K", "requisition_id": "L", "fit_score": "M"}
COLUMNS = [chr(c) for c in range(ord("A"), ord("R") + 1)]
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
# Only the headings this format defines are headings. A cover letter is prose a
# model wrote, and prose contains Markdown — "## Dear Hiring Manager" used to split
# the file and fail the whole role. The cost is that a misspelled section name is
# no longer an error: it reads as body text of the section above it, and that
# section then shows up empty in empty_sections().
SECTION = re.compile(r"^## (cover_letter|why_interested|why_it_fits|resume_tailoring|notes|jd|audit)$", re.M)


class MalformedRoleFile(ValueError):
    """The file does not match the role-file shape. Never guessed at."""


@dataclasses.dataclass
class RoleFile:
    path: pathlib.Path
    fields: dict[str, str]
    sections: dict[str, str]
    jd: str
    audit: str

    def empty_sections(self) -> list[str]:
        return [name for name in PROSE_SECTIONS if not self.sections.get(name, "").strip()]

    def to_row(self) -> list[str]:
        row = {column: "" for column in COLUMNS}
        row.update(self.fields)
        for name, column in SECTION_TO_COLUMN.items():
            row[column] = self.sections.get(name, "").strip()
        if self.audit:
            row["R"] = (row["R"] + "\n\n" + self.audit).strip()
        return [row[c] for c in COLUMNS]


def _posted_phrase(age_hours: float | None) -> str:
    """There is one window, so the phrase names it rather than the role carrying it."""
    if age_hours is None:
        return "unknown (no ATS timestamp)"
    return f"{age_hours:.0f} hours ago; admitted in the {freshness.WINDOW_HOURS}h window"


def write(path, role, *, fit: int, confidence: str, age_hours: float | None,
          run_date: dt.date) -> pathlib.Path:
    path = pathlib.Path(path)
    front = {
        "status": "Discovered",
        "job_url": role.url,
        "date_found": run_date.isoformat(),
        "company": role.company,
        "role": role.title,
        "location": role.location,
        "work_mode": role.work_mode,
        "posted": _posted_phrase(age_hours),
        "freshness_confidence": confidence,
        "requisition_id": role.job_id,
        "fit_score": str(fit),
        "source": role.source,
        "ats": role.ats,
    }
    body = ["---", yaml.safe_dump(front, sort_keys=False, allow_unicode=True).rstrip(), "---", ""]
    for name in PROSE_SECTIONS:
        body += [f"## {name}", "", ""]
    body += ["## jd", "", role.description, ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body))
    return path


def parse(path) -> RoleFile:
    path = pathlib.Path(path)
    text = path.read_text()
    match = FRONT_MATTER.match(text)
    if not match:
        raise MalformedRoleFile(f"{path}: no YAML front matter")
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise MalformedRoleFile(f"{path}: front matter is not valid YAML: {exc}") from exc
    # Valid YAML that is not a mapping. A scalar makes the membership test below
    # raise TypeError, which escapes as a crash rather than as this module's own
    # error — and a caller looping over roles would lose the whole run to one bad
    # file instead of skipping it.
    if not isinstance(front, dict):
        raise MalformedRoleFile(
            f"{path}: front matter is a {type(front).__name__}, not a mapping of facts")
    missing = [f for f in FACT_FIELDS if f not in front]
    if missing:
        raise MalformedRoleFile(f"{path}: missing required fields: {', '.join(missing)}")
    # A key present with no value parses as None, and str(None) is the four letters
    # "None" — which is what would land in the tracker cell. A required fact that is
    # blank is missing, not empty.
    blank = [f for f in FACT_FIELDS if front[f] is None or not str(front[f]).strip()]
    if blank:
        raise MalformedRoleFile(f"{path}: required fields are blank: {', '.join(blank)}")

    body = match.group(2)
    names = SECTION.findall(body)
    # An exact heading repeated is an ambiguity, not a shape to resolve quietly:
    # the dict built below would keep the last one and drop the earlier text with
    # no signal. Step 2 sees these six strings in its own input, so repeating one
    # verbatim is a plausible slip.
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise MalformedRoleFile(f"{path}: repeated section(s): {', '.join(duplicates)}")
    missing_sections = [n for n in (*PROSE_SECTIONS, "jd") if n not in names]
    if missing_sections:
        raise MalformedRoleFile(f"{path}: missing section(s): {', '.join(missing_sections)}")

    chunks = SECTION.split(body)
    sections = {names[i]: chunks[2 + 2 * i].strip() for i in range(len(names))}
    fields = {FIELD_TO_COLUMN[f]: str(front[f]) for f in FACT_FIELDS}
    fields.setdefault("P", "")
    fields.setdefault("Q", "")
    return RoleFile(path=path, fields=fields,
                    sections={n: sections.get(n, "") for n in PROSE_SECTIONS},
                    jd=sections.get("jd", ""), audit=sections.get("audit", ""))
