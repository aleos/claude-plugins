#!/usr/bin/env python3
"""Check a project's decision docs against the decision-docs conventions.

Usage: check.py [PROJECT_ROOT]      (default: current directory)
Exit code: 0 = no errors, 1 = errors found, 2 = no docs/ folder.
Standard library only. Read-only: it never changes files.
"""

import filecmp
import os
import re
import sys
from pathlib import Path

SKILL_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
TEMPLATE_NAMES = ("adr-template-minimal.md", "adr-template.md")
REQUIRED_SECTIONS = (
    "## Context and Problem Statement",
    "## Considered Options",
    "## Decision Outcome",
)
STATUSES = {"proposed", "accepted", "rejected", "deprecated"}
SUPERSEDED = re.compile(r"superseded by ADR-(\d{4})$")
RECORD_NAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
ADR_LINK = re.compile(r"\[[^\]]*?ADR-(\d{4})[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
KIND_FILES = ("README.md", "current-state.md", "open-questions.md")
KIND_DIRS = ("decisions", "research", "guides", "reference")
IMPORTS_AGENTS = re.compile(r"(?:^|\s)@\S*AGENTS\.md")
REGISTRY_ROW = re.compile(r"^\|\s*\[(\d{4})\]\(([^)]+)\)\s*\|.*\|\s*([^|]+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$")


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def front_matter(text):
    """Return the YAML front matter as a flat dict of key: value strings."""
    m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([a-z-]+):\s*(.*?)\s*(?:#.*)?$", line)
        if km:
            fields[km.group(1)] = km.group(2).strip().strip('"')
    return fields


def check_links(root, docs, r):
    for md in sorted(docs.rglob("*.md")):
        if md.parent.name == "decisions" and md.name in TEMPLATE_NAMES:
            continue  # MADR templates link to placeholders
        text = md.read_text()
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target):  # http:, mailto:, …
                continue
            if not (md.parent / target).exists():
                r.error(md.relative_to(root), f"broken link -> {target}")
        for number, target in ADR_LINK.findall(text):
            m = RECORD_NAME.match(Path(target).name)
            if m and m.group(1) != number:
                r.warn(md.relative_to(root), f"link says ADR-{number} but points to {target}")


def check_kinds(root, docs, r):
    """Warn about Markdown files in docs/ that sit in no kind's place."""
    for md in sorted(docs.rglob("*.md")):
        rel = md.relative_to(docs)
        if rel.as_posix() in KIND_FILES or (len(rel.parts) > 1 and rel.parts[0] in KIND_DIRS):
            continue
        r.warn(md.relative_to(root), "fits none of the kinds; move it to one, or into current-state.md")


def check_current_state(root, docs, records, r):
    current = docs / "current-state.md"
    if not current.exists():
        return
    text = current.read_text()
    for rid, (md, status, _) in sorted(records.items()):
        if status == "accepted" and md.name not in text:
            r.warn(current.relative_to(root), f"doesn't cite accepted ADR-{rid} ({md.name})")


def check_records(root, decisions, r):
    """Validate records; return {id: (path, status, date)}."""
    records = {}
    for md in sorted(decisions.glob("[0-9]*.md")):
        where = md.relative_to(root)
        m = RECORD_NAME.match(md.name)
        if not m:
            r.error(where, "file name is not NNNN-title-with-dashes.md")
            continue
        rid, text = m.group(1), md.read_text()
        if rid in records:
            r.error(where, f"duplicate ID {rid}")
        fm = front_matter(text)
        if fm is None:
            r.error(where, "missing front matter")
            fm = {}
        status, date = fm.get("status", ""), fm.get("date", "")
        if not (status in STATUSES or SUPERSEDED.match(status)):
            r.error(where, f"status '{status}' is not one of {sorted(STATUSES)} or 'superseded by ADR-NNNN'")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            r.error(where, f"date '{date}' is not YYYY-MM-DD")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                r.error(where, f"missing section '{section}'")
        records[rid] = (md, status, date)

    ids = sorted(records)
    expected = [f"{i:04d}" for i in range(1, len(ids) + 1)]
    if ids != expected:
        r.error(decisions.relative_to(root), f"IDs not sequential from 0001: {ids}")
    return records


def check_supersede_links(root, records, r):
    for rid, (md, status, _) in records.items():
        m = SUPERSEDED.match(status)
        if not m:
            continue
        new_id = m.group(1)
        if new_id not in records:
            r.error(md.relative_to(root), f"superseded by ADR-{new_id}, which does not exist")
            continue
        new_md = records[new_id][0]
        if md.name not in new_md.read_text():
            r.error(new_md.relative_to(root), f"supersedes ADR-{rid} but does not link {md.name}")
        if new_md.name not in md.read_text():
            r.error(md.relative_to(root), f"does not link forward to {new_md.name}")


def check_registry(root, decisions, records, r):
    registry = decisions / "README.md"
    if not registry.exists():
        r.error(decisions.relative_to(root), "missing README.md registry")
        return
    rows = {}
    for line in registry.read_text().splitlines():
        m = REGISTRY_ROW.match(line)
        if m:
            rows[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    where = registry.relative_to(root)
    for rid, (md, status, date) in records.items():
        if rid not in rows:
            r.error(where, f"no row for ADR-{rid}")
            continue
        link, row_status, row_date = rows[rid]
        if link != md.name:
            r.error(where, f"ADR-{rid} row links {link}, file is {md.name}")
        if (row_status, row_date) != (status, date):
            r.error(where, f"ADR-{rid} row says {row_status} {row_date}, record says {status} {date}")
    for rid in rows.keys() - records.keys():
        r.error(where, f"row for ADR-{rid} but no such record")


def check_templates(root, decisions, r):
    for name in TEMPLATE_NAMES:
        project, bundled = decisions / name, SKILL_TEMPLATES / name
        if not project.exists():
            r.error(decisions.relative_to(root), f"missing template {name}")
        elif bundled.exists() and not filecmp.cmp(project, bundled, shallow=False):
            r.error(project.relative_to(root), "differs from the bundled MADR template")


def check_research(root, docs, r):
    research = docs / "research"
    if not research.is_dir():
        return
    for md in sorted(research.glob("*.md")):
        where = md.relative_to(root)
        if not re.match(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$", md.name):
            r.error(where, "file name is not YYYY-MM-DD-<slug>.md")
        text = md.read_text()
        if "## Outcome" not in text:
            r.error(where, "missing '## Outcome'")
        # Records named in the Outcome should link back to this note.
        outcome = text.split("## Outcome", 1)[-1]
        for target in LINK.findall(outcome):
            rec = (md.parent / target).resolve()
            if rec.exists() and rec.parent.name == "decisions" and md.name not in rec.read_text():
                r.warn(rec.relative_to(root.resolve()), f"is fed by {md.name} but doesn't link it")


def check_agent_rules(root, r):
    agents, claude = root / "AGENTS.md", root / "CLAUDE.md"
    has_rules = lambda p: p.exists() and "## Project documentation" in p.read_text()
    with_rules = [p for p in (agents, claude, root / ".claude" / "CLAUDE.md") if has_rules(p)]
    if not with_rules:
        r.error(root.name or ".", "no '## Project documentation' rules in AGENTS.md, CLAUDE.md or .claude/CLAUDE.md")
    rules = "".join(p.read_text() for p in with_rules)
    for folder in ("guides", "reference"):
        if with_rules and (root / "docs" / folder).is_dir() and f"docs/{folder}/" not in rules:
            r.warn(with_rules[0].relative_to(root), f"the rules have no row for docs/{folder}/, which exists")
    if with_rules != [agents]:
        return
    # Claude Code skips AGENTS.md when one of these exists here or above, unless one imports it.
    # The user's own ~/.claude/CLAUDE.md doesn't count.
    user_file = Path.home() / ".claude" / "CLAUDE.md"
    claude_files = [p for d in (root, *root.parents)
                    for p in (d / "CLAUDE.md", d / ".claude" / "CLAUDE.md", d / "CLAUDE.local.md")
                    if p.exists() and p != user_file]
    if claude_files and not any(IMPORTS_AGENTS.search(p.read_text()) for p in claude_files):
        names = ", ".join(os.path.relpath(p, root) for p in claude_files)
        r.warn("AGENTS.md", f"Claude Code may not read the rules here, because of {names} (no '@AGENTS.md' import)")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    docs, decisions = root / "docs", root / "docs" / "decisions"
    if not docs.is_dir():
        print(f"No docs/ folder in {root}")
        return 2

    r = Report()
    for required in ("README.md", "current-state.md", "open-questions.md"):
        if not (docs / required).exists():
            r.error("docs", f"missing {required}")
    check_links(root, docs, r)
    check_kinds(root, docs, r)
    records = check_records(root, decisions, r) if decisions.is_dir() else {}
    check_supersede_links(root, records, r)
    check_current_state(root, docs, records, r)
    if decisions.is_dir():
        check_registry(root, decisions, records, r)
        check_templates(root, decisions, r)
    check_research(root, docs, r)
    check_agent_rules(root, r)

    for e in r.errors:
        print(f"ERROR   {e}")
    for w in r.warnings:
        print(f"WARNING {w}")
    counts = {}
    for _, status, _ in records.values():
        counts[status] = counts.get(status, 0) + 1
    print(f"\n{len(records)} records {counts or ''} · {len(r.errors)} errors · {len(r.warnings)} warnings")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
