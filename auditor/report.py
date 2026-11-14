"""Write the audit as Markdown."""


def money(x):
    return f"${x:,.0f}" if x is not None else "-"


def table(rows, cols, labels=None, money_cols=()):
    if not rows:
        return "_None._\n"
    labels = labels or cols
    out = ["| " + " | ".join(labels) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        cells = [money(r[c]) if c in money_cols else ("" if r[c] is None else str(r[c])) for c in cols]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def file_check(findings):
    lines = ["# File check", ""]
    for name, f in findings.items():
        if not f["found"]:
            lines.append(f"- **{name}.csv: MISSING.** See docs/export-salesforce-reports.md.")
            continue
        status = "MISSING COLUMNS" if f["missing_required"] else "OK"
        lines.append(f"- **{name}.csv: {status}** ({f['rows']} rows)")
        for col in f["missing_required"]:
            lines.append(f"  - Required column missing: `{col}`")
        for col in f["missing_optional"]:
            from .load import OPTIONAL_NEEDS
            skip = OPTIONAL_NEEDS.get((name, col))
            if skip:
                lines.append(f"  - Optional column missing: `{col}`. Without it: {skip}.")
        renamed = {c: s for c, s in f["mapped"].items() if s != c}
        if renamed:
            lines.append("  - Read as: " + ", ".join(f"'{s}' → {c}" for c, s in renamed.items()))
        if f["problems"]:
            lines.append(f"  - {len(f['problems'])} value problem(s), first ones:")
            lines.extend(f"    - {p}" for p in f["problems"][:5])
    return "\n".join(lines) + "\n"


def audit(h, sourced, influenced, models, results, window_days):
    fix = [r for r in results if r["status"] == "FIX"]
    out = ["# Pipeline attribution audit", ""]
    out.append(f"Influence window: {window_days} days. Influenced pipeline counts only campaign members marked "
               "Responded, on contacts with a role on the deal, who responded before the deal was created.")
    out.append("")

    out.append("## 1. Can you trust the numbers?")
    out.append("")
    out.append("| # | Check | Status | Records | Pipeline affected |")
    out.append("|---|---|---|---|---|")
    for r in results:
        affected = money(r["at_risk_amount"]) if r["at_risk_amount"] else "-"
        status = r["status"] if r["status"] != "SKIPPED" else f"SKIPPED ({r['skipped_because']})"
        out.append(f"| {r['id']} | {r['name']} | {status} | {len(r['rows'])} | {affected} |")
    out.append("")
    out.append(f"{len(fix)} of {len(results)} checks need fixing. 'Pipeline affected' for checks 1-3 is the value of "
               "deals whose influence is undercounted; for check 8 it is how much the influence numbers would be "
               "overstated if non-responders counted. Deals can appear in more than one check.")
    out.append("")

    out.append("## 2. Headline numbers")
    out.append("")
    out.append(f"- Total pipeline: {money(h['pipeline'])} across {h['deals']} deals")
    out.append(f"- Marketing sourced: {money(h['sourced'])} ({h['sourced_pct']:.1f}% of pipeline)")
    out.append(f"- Marketing influenced: {h['influenced_deals']} of {h['deals']} deals "
               f"({h['influenced_deal_pct']:.1f}%), worth {money(h['influenced_pipeline'])}")
    out.append("- Sourced and influenced overlap: one deal can be both. Don't add them together.")
    out.append("")

    out.append("## 3. Sourced pipeline by campaign (Primary Campaign Source, 100% credit)")
    out.append("")
    out.append(table(sourced, ["campaign", "deals", "pipeline"], ["Campaign", "Deals", "Pipeline"], ["pipeline"]))
    out.append("## 4. Influenced pipeline by campaign")
    out.append("")
    out.append("One deal counts under every campaign that touched it, so **these rows don't add up to total pipeline.**")
    out.append("")
    out.append(table(influenced, ["campaign", "deals", "pipeline"], ["Campaign", "Deals", "Pipeline"], ["pipeline"]))
    out.append("## 5. The same deals under three attribution models")
    out.append("")
    out.append(table(models, ["campaign", "first_touch", "last_touch", "even_split"],
                     ["Campaign", "First touch", "Last touch", "Even split"],
                     ["first_touch", "last_touch", "even_split"]))
    out.append("Deals with no influence links (for example, no contact roles) get no credit under any model.")
    out.append("")

    out.append("## 6. Fix list")
    out.append("")
    for r in results:
        if r["status"] not in ("FIX", "INFO"):
            continue
        out.append(f"### Check {r['id']}: {r['name']}")
        out.append("")
        out.append(f"- Why it matters: {r['why']}")
        out.append(f"- Fix: {r['fix']}")
        out.append(f"- More: {r['doc']}")
        out.append("")
        rows = r["rows"]
        cols = list(rows[0].keys())
        mcols = [c for c in cols if c in ("amount",) or c.startswith("pipeline")]
        out.append(table(rows, cols, money_cols=mcols))
    return "\n".join(out)
