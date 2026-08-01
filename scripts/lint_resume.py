#!/usr/bin/env python3
"""lint_resume.py — mechanical checks for a LaTeX resume.

The skill's "Guardrails checklist (run before done)" mixes two kinds of rule:
judgment calls a human must make (is this claim defensible? is the thesis legible?)
and rules a machine can decide (is it one page? is this bullet 140 characters?).
This script owns the second kind only, so the human review can spend itself on the
first kind. It never decides defensibility, essence, or whether a bullet is *good*.

Checks
  page      compile the .tex and assert page count + report leftover vertical space
  lines     per-bullet RENDERED line count and how full the last line is, measured
            from the PDF's own geometry (never from a guessed chars-per-line rule —
            capacity depends on the template's margins and font, so it is measured,
            not assumed). Falls back to a character estimate only with --no-compile.
  verb      bullets that open with a weak/ownerless verb
  stackfirst bullets that open with a tool/stack token
  jargon    bullets whose wording is almost entirely tech tokens (heuristic)
  aitell    banned AI-slop words and phrases
  leak      model self-talk that ended up inside the document (always an error)
  metric    round one-sided percentages with no from->to pair (heuristic)
  forbidden phrases the user's dossier marks off-limits

Usage
  python3 lint_resume.py resume.tex
  python3 lint_resume.py resume.tex --dossier docs/dossier.md
  python3 lint_resume.py resume.tex --no-compile --max-chars 105
  python3 lint_resume.py resume.tex --only page,length

Exit code is 1 if any ERROR-level finding fired, else 0. WARN and NOTE never fail
the run — they are for the human to judge.

Off-limits phrases are read from a fenced block in the dossier:

    ```forbidden-phrases
    a critic/reviewer
    uses the AST call graph
    ```

The block is hand-curated on purpose. A guardrail entry often quotes both the
wrong phrasing and the right one, so only a human can say which is which.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

# --------------------------------------------------------------------------
# vocabularies
# --------------------------------------------------------------------------

WEAK_LEAD_VERBS = {
    "helped", "worked", "assisted", "participated", "involved", "aided",
    "responsible", "supported", "contributed", "collaborated",
}

# Words that read as machine-written to a recruiter who sees hundreds of these.
AI_TELLS = [
    "leveraged", "leveraging", "spearheaded", "facilitated", "utilized",
    "utilizing", "robust", "seamless", "seamlessly", "cutting-edge",
    "state-of-the-art", "innovative", "synergy", "synergies", "passionate about",
    "results-oriented", "results-driven", "proven track record", "best practices",
    "demonstrated ability", "wide range of", "in today's", "delve", "tapestry",
    "testament to", "underscoring", "pivotal", "meticulous", "world-class",
]

# Model self-talk that leaked into the document itself. This is not a style
# question — it is a broken artifact, so it is always an error. The list is
# battle-scarred rather than theoretical: it includes the things a model says
# while failing ("one final attempt", "i keep fabricating"), because those have
# been observed landing in a shipped resume.
LLM_LEAK_PHRASES = [
    "here is the revised", "here is the corrected", "here is the updated",
    "here is my", "below is the", "as requested", "per your feedback",
    "based on your feedback", "as per the instructions",
    "the following resume", "the resume below", "the following cover letter",
    "i have rewritten", "i have removed", "i have updated", "i have corrected",
    "i apologize", "i am sorry", "my mistake", "i made an error",
    "let me try", "one final attempt", "i keep fabricating",
    "note:", "disclaimer:", "important:",
]

# Tokens that mean "this word is stack, not outcome". Lowercased for matching.
TECH_TOKENS = {
    "python", "typescript", "javascript", "java", "golang", "go", "rust", "c++",
    "react", "next.js", "nextjs", "node", "node.js", "django", "flask", "fastapi",
    "express", "tailwind", "nativewind", "redux", "graphql", "rest", "restful",
    "postgresql", "postgres", "mysql", "sqlite", "redis", "mongodb", "firebase",
    "supabase", "chroma", "pinecone", "weaviate", "pgvector", "docker",
    "kubernetes", "k8s", "aws", "gcp", "azure", "terraform", "kafka", "rabbitmq",
    "pytorch", "tensorflow", "langchain", "langgraph", "llamaindex", "autogen",
    "ollama", "openai", "anthropic", "llm", "llms", "rag", "api", "apis", "sdk",
    "jwt", "oauth", "grpc", "websocket", "ci/cd", "playwright", "pytest", "jest",
    "chart.js", "d3", "numpy", "pandas", "spark", "airflow", "dbt", "vector",
    "embedding", "embeddings", "transformer", "multi-agent", "agentic",
}

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "on", "with", "by",
    "from", "at", "as", "into", "across", "over", "that", "which", "it", "its",
    "via", "per", "each", "than", "then", "so", "but", "not", "no", "is", "are",
    "was", "were", "be", "been", "using", "used", "use",
}

DEFAULT_MAX_CHARS = 120      # fallback only; the real capacity is measured from the PDF
DEFAULT_MAX_PAGES = 1
DEFAULT_MAX_LINES = 2
DEFAULT_MIN_TAIL_FILL = 0.35  # a last line thinner than this wastes a whole line

ALL_CHECKS = ("page", "lines", "verb", "stackfirst", "jargon", "aitell",
              "leak", "metric", "forbidden")

ERROR, WARN, NOTE = "ERROR", "WARN", "NOTE"


# --------------------------------------------------------------------------
# LaTeX handling
# --------------------------------------------------------------------------

def strip_comments(tex: str) -> str:
    """Drop % comments but keep escaped \\%."""
    out = []
    for line in tex.splitlines():
        cut = None
        i = 0
        while i < len(line):
            if line[i] == "\\":
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def extract_bullets(tex: str) -> list[tuple[int, str]]:
    """Return (line number, raw LaTeX body) for every \\item in the document body."""
    body = strip_comments(tex)
    start = body.find(r"\begin{document}")
    offset = 0
    if start != -1:
        offset = body[:start].count("\n")
        body = body[start:]

    bullets: list[tuple[int, str]] = []
    current: list[str] | None = None
    current_line = 0
    for idx, line in enumerate(body.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(r"\item"):
            if current is not None:
                bullets.append((current_line, " ".join(current).strip()))
            current = [stripped[len(r"\item"):].strip()]
            current_line = idx + offset
        elif current is not None:
            if stripped.startswith((r"\end{itemize}", r"\begin{", r"\section",
                                    r"\end{document}")) or not stripped:
                bullets.append((current_line, " ".join(current).strip()))
                current = None
            else:
                current.append(stripped)
    if current is not None:
        bullets.append((current_line, " ".join(current).strip()))
    return bullets


def visible_text(latex: str) -> str:
    """Approximate what a reader actually sees for one bullet."""
    s = latex
    s = re.sub(r"\\href\{[^}]*\}\{((?:[^{}]|\{[^}]*\})*)\}", r"\1", s)
    s = re.sub(r"\\(?:textbf|textit|emph|underline|texttt|mbox|textrm)\{"
               r"((?:[^{}]|\{[^}]*\})*)\}", r"\1", s)
    for _ in range(3):  # nested \textbf{\underline{...}}
        new = re.sub(r"\\(?:textbf|textit|emph|underline|texttt)\{"
                     r"((?:[^{}]|\{[^}]*\})*)\}", r"\1", s)
        if new == s:
            break
        s = new
    s = re.sub(r"\$\\approx\$", "~", s)
    s = re.sub(r"\$([^$]*)\$", r"\1", s)          # inline math renders as its body
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)          # leftover commands
    s = s.replace("\\\\", " ").replace("~", " ")
    s = re.sub(r"\\([&%$_#])", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("---", "\u2014").replace("--", "\u2013")
    return re.sub(r"\s+", " ", s).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9\+\.\#/\-]*", text)


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

class Finding:
    def __init__(self, level: str, check: str, line: int, msg: str, ctx: str = ""):
        self.level, self.check, self.line, self.msg, self.ctx = level, check, line, msg, ctx


BULLET_GLYPHS = ("•", "▪", "·", "◦")
CONT_INDENT_TOLERANCE = 24.0   # pt; a continuation line sits just right of its bullet


def pdf_lines(pdf: str) -> list[tuple[float, float, float, str]]:
    """(xMin, xMax, yMin, text) for every rendered line, in reading order."""
    xml = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"],
                         capture_output=True, text=True).stdout
    out = []
    for m in re.finditer(
            r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="[\d.]+">(.*?)</line>',
            xml, re.S):
        text = " ".join(re.findall(r">([^<]*)</word>", m.group(4)))
        text = (text.replace("&amp;", "&").replace("&lt;", "<")
                    .replace("&gt;", ">").replace("&quot;", '"'))
        out.append((float(m.group(1)), float(m.group(3)), float(m.group(2)), text))
    return out


def estimate_line_height(lines) -> float:
    """Median baseline gap between adjacent rendered lines — the cost of one wasted line."""
    gaps = sorted(round(b[2] - a[2], 1) for a, b in zip(lines, lines[1:])
                  if 6.0 < b[2] - a[2] < 24.0)
    return gaps[len(gaps) // 2] if gaps else 13.0


def group_rendered_bullets(lines):
    """Group rendered lines into bullets: a glyph line plus its indented continuations."""
    if not lines:
        return [], 0.0
    right_edge = max(x for _, x, _, _ in lines)
    groups = []
    current = None
    for xmin, xmax, _ymin, text in lines:
        is_bullet = text.lstrip().startswith(BULLET_GLYPHS)
        if is_bullet:
            if current:
                groups.append(current)
            current = {"x": xmin, "lines": [(xmin, xmax, text)]}
        elif current is not None and current["x"] < xmin <= current["x"] + CONT_INDENT_TOLERANCE:
            current["lines"].append((xmin, xmax, text))
        elif current is not None:
            groups.append(current)
            current = None
    if current:
        groups.append(current)
    return groups, right_edge


def check_lines(pdf, bullets, max_lines, min_fill) -> list[Finding]:
    """Measure each bullet as the reader sees it: how many lines, how full the last one."""
    rendered = pdf_lines(pdf)
    if not rendered:
        return [Finding(NOTE, "lines", 0, "pdftotext unavailable — skipped the line measurement")]
    line_height = estimate_line_height(rendered)
    groups, right_edge = group_rendered_bullets(rendered)

    out: list[Finding] = []
    if len(groups) != len(bullets):
        out.append(Finding(NOTE, "lines", 0,
                           f"matched {len(groups)} rendered bullets against {len(bullets)} "
                           f"\\item entries — line numbers below may be off by one"))
    wasted = 0.0
    for i, g in enumerate(groups):
        src_line = bullets[i][0] if i < len(bullets) else 0
        n = len(g["lines"])
        text = g["lines"][0][2]
        if n > max_lines:
            out.append(Finding(ERROR, "lines", src_line,
                               f"renders as {n} lines (limit {max_lines})", text))
            continue
        if n > 1:
            text_left = g["lines"][-1][0]
            fill = (g["lines"][-1][1] - text_left) / (right_edge - text_left)
            if fill < min_fill:
                wasted += line_height
                tail = g["lines"][-1][2]
                to_cut = len(tail.split()) + 2   # the tail itself, plus slack for reflow
                out.append(Finding(
                    WARN, "lines", src_line,
                    f"last line is only {fill:.0%} full — it holds \"{tail}\" and costs a "
                    f"whole line; cut ~{to_cut} words to close it to {n - 1}, or spend the "
                    f"room on something worth a line",
                    text))
    if wasted:
        out.append(Finding(NOTE, "lines", 0,
                           f"~{wasted:.0f}pt is spent on near-empty tail lines "
                           f"(~{wasted / line_height:.0f} lines of the page)"))
    return out


def check_length_fallback(bullets, max_chars) -> list[Finding]:
    """Used only when nothing was compiled. Character capacity is template-dependent."""
    out = [Finding(NOTE, "lines", 0,
                   f"no PDF — estimating against {max_chars} chars/line, which is a guess; "
                   f"compile to measure the real capacity")]
    for line, raw in bullets:
        text = visible_text(raw)
        if len(text) > max_chars * DEFAULT_MAX_LINES:
            out.append(Finding(WARN, "lines", line,
                               f"{len(text)} visible chars — likely over "
                               f"{DEFAULT_MAX_LINES} lines", text))
    return out


def check_verb(bullets) -> list[Finding]:
    out = []
    for line, raw in bullets:
        w = words(visible_text(raw))
        if w and w[0].lower() in WEAK_LEAD_VERBS:
            out.append(Finding(WARN, "verb", line,
                               f"opens with a weak verb: '{w[0]}'", visible_text(raw)))
    return out


def check_stackfirst(bullets) -> list[Finding]:
    out = []
    for line, raw in bullets:
        w = words(visible_text(raw))
        if w and w[0].lower() in TECH_TOKENS:
            out.append(Finding(WARN, "stackfirst", line,
                               f"opens with the stack ('{w[0]}') — lead with the outcome",
                               visible_text(raw)))
    return out


def check_jargon(bullets, threshold=0.45) -> list[Finding]:
    out = []
    for line, raw in bullets:
        text = visible_text(raw)
        w = [x.lower() for x in words(text) if x.lower() not in STOPWORDS]
        if len(w) < 6:
            continue
        tech = sum(1 for x in w if x in TECH_TOKENS)
        ratio = tech / len(w)
        if ratio >= threshold:
            out.append(Finding(WARN, "jargon", line,
                               f"{ratio:.0%} of content words are stack tokens — "
                               f"a generalist screener reads nothing here", text))
    return out


def check_aitell(bullets) -> list[Finding]:
    out = []
    for line, raw in bullets:
        text = visible_text(raw)
        low = text.lower()
        hits = [t for t in AI_TELLS if t in low]
        if hits:
            out.append(Finding(WARN, "aitell", line,
                               "AI-slop wording: " + ", ".join(sorted(hits)), text))
    return out


def check_leak(bullets) -> list[Finding]:
    """Model self-talk in the artifact means the output is broken, not merely styled badly."""
    out = []
    for line, raw in bullets:
        text = visible_text(raw)
        low = text.lower()
        hits = [p for p in LLM_LEAK_PHRASES if p in low]
        if hits:
            out.append(Finding(ERROR, "leak", line,
                               "model self-talk leaked into the resume: "
                               + ", ".join(f'"{h}"' for h in sorted(hits)), text))
    return out


def check_metric(bullets) -> list[Finding]:
    """A lone round percentage with no before/after pair reads as invented."""
    out = []
    two_sided = re.compile(r"\d[\d.,]*\s*(?:ms|s|%|x|k|m)?\s*(?:->|→|to)\s*\d", re.I)
    for line, raw in bullets:
        text = visible_text(raw)
        if two_sided.search(text):
            continue
        for m in re.finditer(r"(\d+)\s*%", text):
            if int(m.group(1)) % 5 == 0:
                out.append(Finding(NOTE, "metric", line,
                                   f"one-sided round metric '{m.group(0)}' — a from→to pair "
                                   f"or an odd true number is harder to doubt", text))
                break
    return out


def load_forbidden(dossier_path: str) -> list[str]:
    if not dossier_path or not os.path.exists(dossier_path):
        return []
    text = open(dossier_path, encoding="utf-8").read()
    m = re.search(r"```forbidden-phrases\s*\n(.*?)```", text, re.S)
    if not m:
        return []
    return [ln.strip() for ln in m.group(1).splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


def check_forbidden(bullets, phrases) -> list[Finding]:
    out = []
    for line, raw in bullets:
        text = visible_text(raw)
        low = text.lower()
        for p in phrases:
            if p.lower() in low:
                out.append(Finding(ERROR, "forbidden", line,
                                   f"off-limits claim from the dossier: '{p}'", text))
    return out


# --------------------------------------------------------------------------
# compile + page geometry
# --------------------------------------------------------------------------

def compile_pdf(tex_path: str, workdir: str) -> tuple[str | None, str]:
    """Compile with whatever engine is on PATH. Returns (pdf_path, note)."""
    src = os.path.abspath(tex_path)
    if shutil.which("tectonic"):
        cmd = ["tectonic", "-X", "compile", src, "--outdir", workdir]
        note = ("compiled with tectonic (XeTeX); Overleaf uses pdfLaTeX, so page breaks "
                "can differ by a hair — trust this while there is >1 line of slack")
    elif shutil.which("pdflatex"):
        cmd = ["pdflatex", "-interaction=nonstopmode", "-output-directory", workdir, src]
        note = "compiled with pdflatex"
    else:
        return None, "no tectonic or pdflatex on PATH — skipping the page check"
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(src) or ".")
    pdf = os.path.join(workdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    if not os.path.exists(pdf):
        tail = (res.stdout + res.stderr).strip().splitlines()[-8:]
        return None, "compile failed:\n    " + "\n    ".join(tail)
    return pdf, note


def page_report(pdf: str, max_pages: int) -> list[Finding]:
    out: list[Finding] = []
    pages = None
    height = 792.0
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.M)
        if m:
            pages = int(m.group(1))
        m = re.search(r"^Page size:\s+[\d.]+ x ([\d.]+)", info, re.M)
        if m:
            height = float(m.group(1))
    if pages is None:
        return [Finding(NOTE, "page", 0, "pdfinfo not available — page count unknown")]

    if pages > max_pages:
        out.append(Finding(ERROR, "page", 0,
                           f"{pages} pages (limit {max_pages}) — cut before anything else"))
    else:
        slack = None
        if shutil.which("pdftotext") and pages == 1:
            bbox = subprocess.run(["pdftotext", "-bbox", pdf, "-"],
                                  capture_output=True, text=True).stdout
            ys = [float(x) for x in re.findall(r'yMax="([\d.]+)"', bbox)]
            if ys:
                # pdftotext bbox origin is the top edge, so the largest yMax is the
                # lowest ink on the page.
                slack = height - 36.0 - max(ys)
        msg = f"{pages} page (limit {max_pages}) — OK"
        if slack is not None:
            msg += f"; ~{slack:.0f}pt of vertical slack left (~{slack / 13:.1f} lines)"
            if slack < 13:
                out.append(Finding(WARN, "page", 0,
                                   "under one line of slack — verify on Overleaf "
                                   "before trusting this verdict"))
        out.append(Finding(NOTE, "page", 0, msg))
    return out


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical guardrail checks for a LaTeX resume.")
    ap.add_argument("tex")
    ap.add_argument("--dossier", default="", help="path to docs/dossier.md for off-limits phrases")
    ap.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS,
                    help="fallback chars/line estimate, used only with --no-compile")
    ap.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    ap.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES,
                    help="rendered lines a single bullet may occupy")
    ap.add_argument("--min-tail-fill", type=float, default=DEFAULT_MIN_TAIL_FILL,
                    help="flag a wrapped bullet whose last line is emptier than this")
    ap.add_argument("--no-compile", action="store_true", help="skip the compile/page check")
    ap.add_argument("--only", default="", help="comma-separated subset of: " + ",".join(ALL_CHECKS))
    args = ap.parse_args()

    if not os.path.exists(args.tex):
        print(f"no such file: {args.tex}", file=sys.stderr)
        return 2

    enabled = set(c.strip() for c in args.only.split(",") if c.strip()) or set(ALL_CHECKS)
    tex = open(args.tex, encoding="utf-8").read()
    bullets = extract_bullets(tex)

    findings: list[Finding] = []
    wants_pdf = not args.no_compile and ({"page", "lines"} & enabled)
    if wants_pdf:
        with tempfile.TemporaryDirectory() as tmp:
            pdf, note = compile_pdf(args.tex, tmp)
            if pdf is None:
                findings.append(Finding(ERROR if "failed" in note else NOTE, "page", 0, note))
            else:
                if "page" in enabled:
                    findings.extend(page_report(pdf, args.max_pages))
                    findings.append(Finding(NOTE, "page", 0, note))
                if "lines" in enabled:
                    findings += check_lines(pdf, bullets, args.max_lines, args.min_tail_fill)
    elif "lines" in enabled:
        findings += check_length_fallback(bullets, args.max_chars)

    if "verb" in enabled:
        findings += check_verb(bullets)
    if "stackfirst" in enabled:
        findings += check_stackfirst(bullets)
    if "jargon" in enabled:
        findings += check_jargon(bullets)
    if "aitell" in enabled:
        findings += check_aitell(bullets)
    if "leak" in enabled:
        findings += check_leak(bullets)
    if "metric" in enabled:
        findings += check_metric(bullets)
    if "forbidden" in enabled:
        findings += check_forbidden(bullets, load_forbidden(args.dossier))

    order = {ERROR: 0, WARN: 1, NOTE: 2}
    findings.sort(key=lambda f: (order[f.level], f.line))

    print(f"lint_resume: {args.tex} — {len(bullets)} bullets\n")
    for f in findings:
        where = f"{args.tex}:{f.line}" if f.line else args.tex
        print(f"[{f.level:5}] {f.check:10} {where}  {f.msg}")
        if f.ctx:
            print(f"            > {f.ctx[:120]}")
    errors = sum(1 for f in findings if f.level == ERROR)
    warns = sum(1 for f in findings if f.level == WARN)
    print(f"\n{errors} error(s), {warns} warning(s). "
          f"Mechanical checks only — defensibility, essence and spine are still a human read.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
