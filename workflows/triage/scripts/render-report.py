#!/usr/bin/env python3
"""Render triage report from triaged_issues.json and templates.

This script performs deterministic placeholder replacement on the HTML
and Markdown templates using structured triage data. It contains NO
triage logic -- only rendering.

Usage:
    python3 scripts/render-report.py \\
        --data artifacts/triage/triaged_issues.json \\
        --output artifacts/triage/ \\
        --templates templates/
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_template(path):
    with open(path, "r") as f:
        return f.read()


def compute_stats(issues):
    """Count issues per recommendation type."""
    types = [
        "CLOSE", "FIX_NOW", "BACKLOG", "NEEDS_INFO",
        "DUPLICATE", "CBA_AUTO", "ASSIGN", "WONT_FIX",
    ]
    return {t: sum(1 for i in issues if i.get("recommendation") == t) for t in types}


def render_html(template, data):
    """Replace all placeholders in the HTML template."""
    metadata = data["metadata"]
    issues = data["issues"]
    stats = compute_stats(issues)

    replacements = {
        "{REPO_URL}": metadata.get("url", ""),
        "{REPO_NAME}": metadata.get("name", ""),
        "{DATE}": metadata.get("date", datetime.now().strftime("%Y-%m-%d")),
        "{TOTAL_ISSUES}": str(metadata.get("totalIssues", len(issues))),
        "{CLOSE_COUNT}": str(stats["CLOSE"]),
        "{FIX_NOW_COUNT}": str(stats["FIX_NOW"]),
        "{BACKLOG_COUNT}": str(stats["BACKLOG"]),
        "{NEEDS_INFO_COUNT}": str(stats["NEEDS_INFO"]),
        "{AMBER_AUTO_COUNT}": str(stats["CBA_AUTO"]),
        "{ASSIGN_COUNT}": str(stats["ASSIGN"]),
        "{DUPLICATE_COUNT}": str(stats["DUPLICATE"]),
        "{WONT_FIX_COUNT}": str(stats["WONT_FIX"]),
        "{ISSUES_JSON}": json.dumps(issues),
        "{METADATA_JSON}": json.dumps(metadata),
        "{TABLE_ROWS}": "",  # Table is rendered client-side by JS
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def render_markdown(template, data):
    """Replace all placeholders in the Markdown template."""
    metadata = data["metadata"]
    issues = data["issues"]
    stats = compute_stats(issues)

    # Build issue rows for the table
    issue_rows = []
    for issue in sorted(issues, key=lambda x: x.get("recommendation", "")):
        title = issue.get("title", "")
        if len(title) > 60:
            title = title[:57] + "..."
        reason = issue.get("reason", "")
        if len(reason) > 40:
            reason = reason[:37] + "..."
        next_action = issue.get("nextAction", "")
        if len(next_action) > 40:
            next_action = next_action[:37] + "..."

        row = (
            f"| {issue.get('number', '')} "
            f"| {title} "
            f"| {issue.get('type', '')} "
            f"| {issue.get('priority', '')} "
            f"| {issue.get('status', 'open')} "
            f"| {issue.get('recommendation', '')} "
            f"| {reason} "
            f"| {issue.get('waitingOn', '-')} "
            f"| {next_action} |"
        )
        issue_rows.append(row)

    # Build detail sections per recommendation
    def detail_section(rec_type):
        matched = [i for i in issues if i.get("recommendation") == rec_type]
        if not matched:
            return "_None_"
        lines = []
        for i in matched:
            lines.append(f"- **#{i['number']}** {i['title']}: {i.get('reason', '')}")
        return "\n".join(lines)

    # Build quick wins (FIX_NOW items)
    fix_now = [i for i in issues if i.get("recommendation") == "FIX_NOW"]
    if fix_now:
        quick_wins = "\n".join(
            f"- **#{i['number']}** {i['title']}" for i in fix_now
        )
    else:
        quick_wins = "_None identified_"

    # Build clusters (group by type)
    clusters_by_type = {}
    for i in issues:
        t = i.get("type", "other")
        clusters_by_type.setdefault(t, []).append(i)
    cluster_lines = []
    for t, items in clusters_by_type.items():
        cluster_lines.append(f"- **{t.capitalize()}** ({len(items)} issues)")
    clusters = "\n".join(cluster_lines) if cluster_lines else "_No clusters_"

    replacements = {
        "{REPO_URL}": metadata.get("url", ""),
        "{DATE}": metadata.get("date", datetime.now().strftime("%Y-%m-%d")),
        "{TOTAL_ISSUES}": str(metadata.get("totalIssues", len(issues))),
        "{ANALYZED_COUNT}": str(len(issues)),
        "{CLOSE_COUNT}": str(stats["CLOSE"]),
        "{FIX_NOW_COUNT}": str(stats["FIX_NOW"]),
        "{BACKLOG_COUNT}": str(stats["BACKLOG"]),
        "{NEEDS_INFO_COUNT}": str(stats["NEEDS_INFO"]),
        "{AMBER_AUTO_COUNT}": str(stats["CBA_AUTO"]),
        "{ASSIGN_COUNT}": str(stats["ASSIGN"]),
        "{WONT_FIX_COUNT}": str(stats["WONT_FIX"]),
        "{ISSUE_ROWS}": "\n".join(issue_rows),
        "{CLOSE_DETAILS}": detail_section("CLOSE"),
        "{FIX_NOW_DETAILS}": detail_section("FIX_NOW"),
        "{NEEDS_INFO_DETAILS}": detail_section("NEEDS_INFO"),
        "{DUPLICATE_DETAILS}": detail_section("DUPLICATE"),
        "{AMBER_AUTO_DETAILS}": detail_section("CBA_AUTO"),
        "{QUICK_WINS}": quick_wins,
        "{CLUSTERS}": clusters,
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Render triage report from data and templates"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to triaged_issues.json",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for rendered reports",
    )
    parser.add_argument(
        "--templates",
        required=True,
        help="Directory containing report.html and triage-report.md templates",
    )

    args = parser.parse_args()

    # Validate inputs
    if not os.path.isfile(args.data):
        print(f"Error: Data file not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    html_template_path = os.path.join(args.templates, "report.html")
    md_template_path = os.path.join(args.templates, "triage-report.md")

    if not os.path.isfile(html_template_path):
        print(f"Error: HTML template not found: {html_template_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(md_template_path):
        print(f"Error: Markdown template not found: {md_template_path}", file=sys.stderr)
        sys.exit(1)

    # Load data and templates
    data = load_json(args.data)
    html_template = load_template(html_template_path)
    md_template = load_template(md_template_path)

    # Validate data structure
    if "metadata" not in data or "issues" not in data:
        print(
            'Error: Data file must contain "metadata" and "issues" keys',
            file=sys.stderr,
        )
        sys.exit(1)

    # Render
    html_output = render_html(html_template, data)
    md_output = render_markdown(md_template, data)

    # Write outputs
    os.makedirs(args.output, exist_ok=True)

    html_out_path = os.path.join(args.output, "report.html")
    md_out_path = os.path.join(args.output, "triage-report.md")

    with open(html_out_path, "w") as f:
        f.write(html_output)

    with open(md_out_path, "w") as f:
        f.write(md_output)

    stats = compute_stats(data["issues"])
    print(f"Rendered {len(data['issues'])} issues")
    print(f"  HTML report: {html_out_path}")
    print(f"  Markdown report: {md_out_path}")
    print(f"  Stats: {json.dumps(stats)}")


if __name__ == "__main__":
    main()
