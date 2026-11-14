"""Command line: guide, check-files, audit."""
import argparse
import sys
from pathlib import Path

from . import load, checks, report

GUIDE = """Export these 7 Salesforce reports as CSV (Details Only) into one folder,
named exactly as below. Full column list: docs/export-salesforce-reports.md

  opportunities.csv              Opportunities report
  opportunity_contact_roles.csv  Opportunities with Contact Roles report
  campaign_members.csv           Campaigns with Campaign Members report
  campaigns.csv                  Campaigns report
  contacts.csv                   Contacts & Accounts report
  leads.csv                      Leads report (include converted leads)
  accounts.csv                   Accounts report

Then run:  python3 -m auditor check-files <folder>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="auditor",
                                 description="Audit B2B pipeline attribution from Salesforce report exports.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("guide", help="which Salesforce reports to export")
    c = sub.add_parser("check-files", help="check the export folder before auditing")
    c.add_argument("folder")
    a = sub.add_parser("audit", help="run the checks and pipeline numbers")
    a.add_argument("folder")
    a.add_argument("--window", type=int, default=180, help="influence window in days (default 180)")
    a.add_argument("--out", help="also save the report to this Markdown file")
    args = ap.parse_args(argv)

    if args.cmd == "guide":
        print(GUIDE)
        return 0

    if not Path(args.folder).is_dir():
        print(f"Folder not found: {args.folder}")
        return 2
    tables, findings = load.read_folder(args.folder)

    if args.cmd == "check-files":
        print(report.file_check(findings))
        if load.ready(findings):
            print("Ready to audit.")
            return 0
        print("Not ready: fix the missing files or columns above first.")
        return 1

    if not load.ready(findings):
        print(report.file_check(findings))
        print("Not ready: fix the missing files or columns above first.")
        return 1
    db = load.to_sqlite(tables, args.window)
    checks.prepare(db)
    text = report.audit(checks.headline(db), checks.sourced_by_campaign(db), checks.influenced_by_campaign(db),
                        checks.attribution_models(db), checks.run_checks(db, findings), args.window)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"\nSaved to {args.out}", file=sys.stderr)
    return 0
