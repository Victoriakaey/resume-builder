#!/usr/bin/env python3
"""Hand the resume to a reader who knows nothing, and see what they can tell you.

The mechanical checks in `lint_resume.py` assert things about the FILE: one page,
no typos, no bullet spilling onto a second line, no phrase the dossier forbids.
None of them can catch the failure that matters most, because it is a property of
the reader and not of the file — an entry can be clean, measured, correctly spelled
and still leave a first-time reader unable to say what the thing IS.

That failure is testable, but only if the test is a QUESTION with a checkable
answer rather than a score. Two measured findings decide the shape:

  · Recruiter judgement is close to a coin flip (55% correct, Fleiss kappa 0.13,
    two recruiters 41 points apart on the same resume). A critic asked to predict
    whether a resume passes is simulating a coin, and will do it confidently.
  · An open-sourced ATS scored one unchanged resume between 66 and 99 across 100
    runs. Scoring is noise at this granularity.

So this script never asks for a score and never asks for a prediction. It asks a
cold reader to ANSWER, and the pass/fail is computed here in Python by matching
required concepts. The model contributes prose; it never contributes a verdict.

Isolation matters more than it looks. The reader runs in a throwaway directory
with a replaced system prompt so that no CLAUDE.md, no repo, no dossier and no
conversation leaks in — otherwise it "knows" what the product is for the same
reason the author does, and the test passes while the resume still fails.

Usage:
  python3 cold_read.py resume.tex --expect docs/cold-read.json
  python3 cold_read.py resume.tex --expect docs/cold-read.json --raw
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The reader is asked what a screener would want and could plausibly extract. The
# last question is the one that pays: it turns "I could not tell" into a list.
DEFAULT_QUESTIONS = {
    "product": "What does this person's CURRENT employer make? Name the kind of "
               "product in one short phrase (e.g. 'a mobile banking app').",
    "built": "What did this person personally BUILD at that employer? List the "
             "concrete things, not the adjectives.",
    "stack": "What technologies did they use there? List only ones the resume names.",
    "users": "Who uses the things they built? Name them, or say 'not stated'.",
    "scale": "Is there any evidence the work was used or measured at real scale? "
             "Quote the numbers if so.",
    "unclear": "List everything you could NOT tell from this resume that a hiring "
               "manager would want to know. Be specific and blunt.",
}

SYSTEM_PROMPT = (
    "You are reading a resume you have never seen, for a company you have never "
    "heard of. You know nothing about this person or their projects beyond the "
    "text you are given. Never guess to be helpful: if the resume does not say "
    "something, answer 'not stated'. Answer only from the text."
)

# Which CLI to read with. Reading the same page with a DIFFERENT model lineage is
# the strongest version of this test: three Claude readers share Claude's blind
# spots, so three agreements are worth less than they look. Only `claude` accepts
# a replaced system prompt and a tool denylist as flags — for the others the same
# instruction is prepended to the user prompt instead, which is weaker isolation
# but still a reader that has never seen this repo.
CLI_SHAPES = {
    "claude": {
        "argv": lambda prompt, model: (
            ["claude", "-p", prompt, "--model", model, "--system-prompt", SYSTEM_PROMPT,
             "--disallowed-tools", "Bash", "Read", "Edit", "Write", "Glob", "Grep",
             "WebFetch", "WebSearch", "Task"]
        ),
        "inline_system": False,
        "default_model": "sonnet",
    },
    # --skip-git-repo-check is required, not optional: the reader deliberately runs
    # in a throwaway directory, which is exactly the "not a trusted git repo" case
    # codex refuses by default. Without it the run dies with an empty stdout.
    "codex": {
        "argv": lambda prompt, model: ["codex", "exec", "--skip-git-repo-check", prompt],
        "inline_system": True,
        "default_model": "",
    },
    "gemini": {
        "argv": lambda prompt, model: ["gemini", "-p", prompt],
        "inline_system": True,
        "default_model": "",
    },
    "agy": {
        "argv": lambda prompt, model: ["agy", "--print", prompt],
        "inline_system": True,
        "default_model": "",
    },
}


# --------------------------------------------------------------------------
# resume -> plain text
# --------------------------------------------------------------------------

def tex_to_text(tex_path: str) -> str:
    """Render the resume and read back what a text extractor sees.

    Deliberately goes through the PDF rather than stripping LaTeX: the reader
    should see what an ATS or a human sees, including anything the template
    silently drops.
    """
    for engine in (["tectonic", "-o"], ["pdflatex", "-output-directory"]):
        if shutil.which(engine[0]) is None:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            cmd = ([engine[0], engine[1], tmp, os.path.abspath(tex_path)]
                   if engine[0] == "tectonic" else
                   [engine[0], "-interaction=nonstopmode", engine[1], tmp,
                    os.path.abspath(tex_path)])
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  cwd=os.path.dirname(os.path.abspath(tex_path)) or ".")
            pdf = os.path.join(tmp, os.path.splitext(os.path.basename(tex_path))[0] + ".pdf")
            if not os.path.exists(pdf):
                continue
            if shutil.which("pdftotext") is None:
                raise SystemExit("pdftotext not found — install poppler")
            out = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                                 capture_output=True, text=True)
            if out.stdout.strip():
                return out.stdout
            _ = proc
    raise SystemExit(f"could not render {tex_path} to text")


# --------------------------------------------------------------------------
# the cold reader
# --------------------------------------------------------------------------

def ask_cold_reader(resume_text: str, questions: dict, model: str,
                    cli: str = "claude") -> dict:
    """Run one reader with no context and return its answers keyed by question id.

    Runs in a throwaway cwd so no CLAUDE.md is discovered, and — on the CLIs that
    take it as a flag — replaces the system prompt so the default one, which
    carries environment and memory, is never used.
    """
    shape = CLI_SHAPES.get(cli)
    if shape is None:
        raise SystemExit(f"unknown --cli {cli!r}; known: {', '.join(CLI_SHAPES)}")

    numbered = "\n".join(f"- {qid}: {text}" for qid, text in questions.items())
    prompt = (
        (SYSTEM_PROMPT + "\n\n" if shape["inline_system"] else "")
        + "Here is the full text of a resume:\n\n"
        "<resume>\n" + resume_text.strip() + "\n</resume>\n\n"
        "Answer each question below from that text alone.\n\n"
        + numbered + "\n\n"
        "Reply with ONLY a JSON object mapping each question id to your answer "
        "string. No preamble, no code fence."
    )

    with tempfile.TemporaryDirectory() as sandbox:
        try:
            proc = subprocess.run(
                shape["argv"](prompt, model or shape["default_model"]),
                capture_output=True, text=True, cwd=sandbox, timeout=300,
            )
        except FileNotFoundError:
            raise SystemExit(f"`{cli}` CLI not found on PATH")
        except subprocess.TimeoutExpired:
            raise SystemExit(f"{cli} cold reader timed out after 300s")

    raw = (proc.stdout or "").strip()
    if not raw:
        raise SystemExit(f"{cli} cold reader returned nothing.\n{proc.stderr[-800:]}")
    return parse_answers(raw, questions)


def parse_answers(raw: str, questions: dict) -> dict:
    """Model output is untrusted input: never let a parse failure look like a pass.

    A missing or unparseable answer becomes the empty string, which fails every
    concept match downstream — the safe direction. Silently treating it as a pass
    would make a broken run indistinguishable from a good resume.
    """
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    obj = None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        brace = re.search(r"\{.*\}", text, re.S)
        if brace:
            try:
                obj = json.loads(brace.group(0))
            except json.JSONDecodeError:
                obj = None
    if not isinstance(obj, dict):
        return {qid: "" for qid in questions} | {"_unparsed": raw}
    return {qid: str(obj.get(qid, "") or "") for qid in questions}


# --------------------------------------------------------------------------
# verdict — computed here, never by the model
# --------------------------------------------------------------------------

def check_expectations(runs: list[dict], expect: dict) -> list[dict]:
    """Match each required concept against the readers' answers, in code.

    `any_of` entries are regexes; a concept is conveyed in a run if any of them
    appears in that run's answer. The model never sees the expectations, so it
    cannot write to the test.

    Takes a LIST of runs and requires a majority, because one reader is not a
    test. The first version of this script asked once, and a concept that had
    been reported in one run went missing in the next on a byte-identical resume
    — the same non-determinism this whole approach exists to route around. A
    single miss is now a minority report, not a failure.
    """
    n = len(runs) or 1
    need = n // 2 + 1
    misses = []
    for qid, spec in expect.get("questions", {}).items():
        for concept in spec.get("must_convey", []):
            pats = concept.get("any_of", [])
            hits = sum(1 for r in runs
                       if any(re.search(p, r.get(qid, ""), re.I) for p in pats))
            if hits < need:
                sample = next((r.get(qid, "") for r in runs
                               if not any(re.search(p, r.get(qid, ""), re.I) for p in pats)), "")
                misses.append({"question": qid, "label": concept.get("label", ""),
                               "answer": sample, "hits": hits, "runs": n})
    return misses


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tex")
    ap.add_argument("--expect", default="", help="path to the expectations JSON")
    ap.add_argument("--cli", default="claude",
                    help="which agent CLI reads the page: " + ", ".join(CLI_SHAPES))
    ap.add_argument("--model", default="",
                    help="model override; defaults per --cli")
    ap.add_argument("--runs", type=int, default=3,
                    help="independent cold readers; a concept must survive a majority")
    ap.add_argument("--raw", action="store_true", help="print every answer, not just misses")
    args = ap.parse_args()

    if not os.path.exists(args.tex):
        print(f"no such file: {args.tex}", file=sys.stderr)
        return 2

    expect = {}
    if args.expect:
        if not os.path.exists(args.expect):
            print(f"no such expectations file: {args.expect}", file=sys.stderr)
            return 2
        expect = json.loads(open(args.expect, encoding="utf-8").read())

    questions = dict(DEFAULT_QUESTIONS)
    questions.update(expect.get("extra_questions", {}))

    resume_text = tex_to_text(args.tex)
    n = max(1, args.runs if expect else 1)
    runs = []
    for i in range(n):
        answers = ask_cold_reader(resume_text, questions, args.model, args.cli)
        runs.append(answers)
        if "_unparsed" in answers:
            print(f"reader {i + 1} did not return JSON — every concept counts as "
                  f"unconveyed for this run\n")
            print(answers["_unparsed"][:1200] + "\n")

    if args.raw or not expect:
        for i, answers in enumerate(runs, start=1):
            if n > 1:
                print(f"════ reader {i} of {n}")
            for qid, text in questions.items():
                print(f"── {qid}: {text}")
                print(f"   {answers.get(qid, '').strip() or '(no answer)'}\n")

    if not expect:
        print("no expectations file given — answers only, nothing asserted")
        return 0

    misses = check_expectations(runs, expect)
    if not misses:
        print(f"{n} cold readers, majority conveyed every required concept.")
        return 0

    print(f"{len(misses)} concept(s) a majority of {n} cold readers could not get "
          f"from the page:\n")
    for m in misses:
        print(f"  [{m['question']}] {m['label']}  ({m['hits']}/{m['runs']} readers got it)")
        got = m["answer"].strip().replace("\n", " ")
        print(f"      a reader who missed it said: {got[:160] or '(nothing)'}\n")
    # Not an error exit: this is a diagnosis, not a gate. The mechanical gate is
    # lint_resume.py; this one is for reading and deciding.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
