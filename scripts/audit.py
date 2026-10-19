#!/usr/bin/env python3
"""Heuristic audit of a Claude Code setup, from a token point of view.

Measures what is measurable and flags what is oversized. It does not judge
content quality: a short CLAUDE.md can still be bad, and this script won't see it.

Usage:
    python audit.py [path]           markdown report
    python audit.py [path] --json    JSON output
    python audit.py [path] --global  include user-level skills

Standard library only, Python 3.9+.
"""

import json
import os
import sys

SKIP_DIRS = {
    "node_modules", ".git", ".venv", "venv", "env", "dist", "build", "out",
    "target", "vendor", "__pycache__", ".next", ".nuxt", ".cache", ".tox",
    "coverage", ".mypy_cache", ".pytest_cache", "site-packages", ".terraform",
}

MAX_DEPTH = 3

# Thresholds in "estimated tokens" (chars / 4). Orders of magnitude, not measurements.
CLAUDE_MD_WARN = 1200
CLAUDE_MD_HIGH = 3000

NOISY_FLAGS = ("--reporter", "--quiet", "--silent", "-q", "--tap", "dot", "--compact")
NOISY_HINTS = ("test", "vitest", "jest", "pytest", "mocha", "nx test", "run test")


def walk(root):
    """Yield (dirpath, filenames), skipping build and dependency directories."""
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if depth >= MAX_DEPTH:
            dirnames[:] = []
        yield dirpath, filenames


def estimate_tokens(text):
    return int(len(text) / 4)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def find_claude_md(root):
    """Find CLAUDE.md files, including .claude/CLAUDE.md, ignoring dependencies."""
    found = []
    for dirpath, filenames in walk(root):
        for name in filenames:
            if name.upper() != "CLAUDE.MD":
                continue
            full = os.path.join(dirpath, name)
            text = read_text(full)
            found.append({
                "path": os.path.relpath(full, root).replace(os.sep, "/"),
                "chars": len(text),
                "lines": text.count("\n") + 1 if text else 0,
                "tokens_estimate": estimate_tokens(text),
                "imports": text.count("@"),
            })
    found.sort(key=lambda item: item["tokens_estimate"], reverse=True)
    return found


def find_mcp_servers(root):
    """Count MCP servers declared in the usual config files."""
    candidates = [
        ".mcp.json",
        "mcp.json",
        ".claude/settings.json",
        ".claude/settings.local.json",
        ".claude.json",
        "claude_desktop_config.json",
    ]
    servers = {}
    for rel in candidates:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        for key in ("mcpServers", "servers"):
            block = data.get(key)
            if isinstance(block, dict):
                for name in block:
                    servers.setdefault(name, rel)
        for key in ("enabledMcpServers", "allowedMcpServers", "disabledMcpServers"):
            block = data.get(key)
            if isinstance(block, list):
                for name in block:
                    if isinstance(name, str):
                        servers.setdefault(name, rel)
    return servers


def find_skills(root, include_global=False):
    """Count local skills (SKILL.md), plus user-level ones when asked."""
    skills = []
    for dirpath, filenames in walk(root):
        for name in filenames:
            if name == "SKILL.md":
                rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
                skills.append(rel)
    if include_global:
        home = os.path.expanduser("~")
        for base in (".claude/skills", ".config/opencode/skills"):
            path = os.path.join(home, base)
            if not os.path.isdir(path):
                continue
            for entry in sorted(os.listdir(path)):
                candidate = os.path.join(path, entry, "SKILL.md")
                if os.path.isfile(candidate):
                    skills.append("~/%s/%s/SKILL.md" % (base, entry))
    return skills


def find_noisy_commands(root):
    """Flag test scripts that will produce noise in the conversation."""
    noisy = []
    for dirpath, filenames in walk(root):
        if "package.json" not in filenames:
            continue
        path = os.path.join(dirpath, "package.json")
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        scripts = data.get("scripts")
        if not isinstance(scripts, dict):
            continue
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        for name, cmd in scripts.items():
            if not isinstance(cmd, str):
                continue
            low = cmd.lower()
            if not any(hint in low or hint in name.lower() for hint in NOISY_HINTS):
                continue
            if "watch" in low or "watch" in name.lower():
                continue  # interactive by nature, never read by the model
            if any(flag in low for flag in NOISY_FLAGS):
                continue
            noisy.append({"package": rel, "script": name, "command": cmd})
    return noisy


def find_telemetry(root):
    """Look for a telemetry configuration (needed to track cache reads)."""
    for rel in (".claude/settings.json", ".claude/settings.local.json", ".mcp.json"):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        text = read_text(path)
        if "CLAUDE_CODE_ENABLE_TELEMETRY" in text or "OTEL_EXPORTER" in text:
            return rel
    return None


def severity(tokens):
    if tokens >= CLAUDE_MD_HIGH:
        return "high"
    if tokens >= CLAUDE_MD_WARN:
        return "warn"
    return "ok"


def build_report(root, include_global):
    root = os.path.abspath(root)
    claude_mds = find_claude_md(root)
    servers = find_mcp_servers(root)
    skills = find_skills(root, include_global)
    noisy = find_noisy_commands(root)
    telemetry = find_telemetry(root)

    prefix_tokens = sum(item["tokens_estimate"] for item in claude_mds)
    findings = []

    for item in claude_mds:
        level = severity(item["tokens_estimate"])
        if level == "high":
            findings.append({
                "level": "high",
                "title": "Oversized CLAUDE.md: %s (~%d estimated tokens)" % (item["path"], item["tokens_estimate"]),
                "detail": "Charged on every request of every session. Move the sections that don't serve every task "
                          "into skills, which load nothing but their name and description.",
            })
        elif level == "warn":
            findings.append({
                "level": "warn",
                "title": "CLAUDE.md worth watching: %s (~%d estimated tokens)" % (item["path"], item["tokens_estimate"]),
                "detail": "Check that every line serves every task. Instructions that newer models no longer need are "
                          "the easiest win.",
            })

    if len(servers) > 5:
        findings.append({
            "level": "warn",
            "title": "%d MCP servers declared" % len(servers),
            "detail": "Idle servers cost little, but not nothing. Switch them off per session with /mcp, restrict "
                      "with allowedMcpServers, or replace with a CLI where one exists.",
        })

    for item in noisy:
        findings.append({
            "level": "warn",
            "title": "Noisy test script: %s -> %s" % (item["package"], item["script"]),
            "detail": "`%s`: the output stays in the conversation for the rest of the session. "
                      "Add a compact reporter and document the command in CLAUDE.md." % item["command"][:90],
        })

    if not telemetry and (len(claude_mds) or len(servers)):
        findings.append({
            "level": "info",
            "title": "No telemetry detected",
            "detail": "Without OpenTelemetry, the cache-read share per person stays invisible. "
                      "Two environment variables are enough to turn it on.",
        })

    if not claude_mds and not servers and not skills:
        findings.append({
            "level": "info",
            "title": "No Claude Code configuration found",
            "detail": "No CLAUDE.md, no MCP server, no skill. That is a healthy starting state: only add context "
                      "when it serves every task.",
        })

    order = {"high": 0, "warn": 1, "info": 2}
    findings.sort(key=lambda item: order.get(item["level"], 3))

    return {
        "root": root,
        "figures": {
            "claude_md_count": len(claude_mds),
            "claude_md_prefix_tokens_estimate": prefix_tokens,
            "mcp_servers": len(servers),
            "skills": len(skills),
            "noisy_scripts": len(noisy),
            "telemetry": telemetry,
        },
        "claude_mds": claude_mds,
        "servers": [{"name": name, "file": src} for name, src in sorted(servers.items())],
        "skills": skills,
        "noisy_scripts": noisy,
        "findings": findings,
    }


def render_markdown(report):
    fig = report["figures"]
    lines = []
    lines.append("# Claude Code audit — tokens and cache")
    lines.append("")
    lines.append("Root: `%s`" % report["root"])
    lines.append("")
    lines.append("## Figures")
    lines.append("")
    lines.append("| Measure | Value |")
    lines.append("|---|---|")
    lines.append("| CLAUDE.md files | %d |" % fig["claude_md_count"])
    lines.append("| Estimated prefix (CLAUDE.md only) | ~%d tokens |" % fig["claude_md_prefix_tokens_estimate"])
    lines.append("| MCP servers declared | %d |" % fig["mcp_servers"])
    lines.append("| Local skills | %d |" % fig["skills"])
    lines.append("| Noisy test scripts | %d |" % fig["noisy_scripts"])
    lines.append("| Telemetry | %s |" % (fig["telemetry"] or "not detected"))
    lines.append("")

    if report["claude_mds"]:
        lines.append("## CLAUDE.md files")
        lines.append("")
        lines.append("| File | Lines | ~Tokens | Level |")
        lines.append("|---|---:|---:|---|")
        for item in report["claude_mds"]:
            lines.append("| `%s` | %d | %d | %s |" % (
                item["path"], item["lines"], item["tokens_estimate"], severity(item["tokens_estimate"])))
        lines.append("")

    if report["findings"]:
        lines.append("## Findings")
        lines.append("")
        for item in report["findings"]:
            lines.append("- **[%s]** %s" % (item["level"], item["title"]))
            lines.append("  %s" % item["detail"])
        lines.append("")

    if report["skills"]:
        lines.append("## Local skills")
        lines.append("")
        for name in report["skills"]:
            lines.append("- `%s`" % name)
        lines.append("")

    lines.append("## Limits of this audit")
    lines.append("")
    lines.append("- Tokens are estimated as `characters / 4`. That is not a tokenizer, it is an order of magnitude.")
    lines.append("- The script measures sizes, not quality. It cannot tell whether a CLAUDE.md is useful.")
    lines.append("- The cache cannot be measured offline: read `/usage` (cache-read share) and, for teams, the")
    lines.append("  OpenTelemetry data. Those are the only real figures for the prefix and the TTL.")
    lines.append("")
    return "\n".join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    root = args[0] if args else os.getcwd()
    if not os.path.isdir(root):
        sys.stderr.write("Path not found: %s\n" % root)
        return 2
    report = build_report(root, include_global="--global" in flags)
    if "--json" in flags:
        sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(render_markdown(report) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv))
