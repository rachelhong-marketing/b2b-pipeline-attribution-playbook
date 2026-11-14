"""Read Salesforce report exports (CSV) into an in-memory SQLite database.

Accepts the column names used in data/ and the usual Salesforce report labels
("Opportunity ID", "Primary Campaign Source", "First Responded Date", ...).
Cleans dates, amounts, checkboxes, 18-character IDs and website domains.
"""
import csv
import re
import sqlite3
from datetime import datetime
from pathlib import Path

# kind: id, text, date, money, bool, email, domain
# Each column: (kind, required, [accepted header labels])
FILES = {
    "opportunities": {
        "report": "Opportunities",
        "columns": {
            "opportunity_id": ("id", True, ["Opportunity ID"]),
            "account_id": ("id", True, ["Account ID"]),
            "opportunity_name": ("text", True, ["Opportunity Name"]),
            "amount": ("money", True, ["Amount"]),
            "stage": ("text", True, ["Stage"]),
            "is_closed": ("bool", True, ["Closed"]),
            "is_won": ("bool", False, ["Won"]),
            "created_date": ("date", True, ["Created Date"]),
            "close_date": ("date", False, ["Close Date"]),
            "primary_campaign_id": ("id", False, ["Primary Campaign Source", "Primary Campaign ID", "Primary Campaign"]),
        },
    },
    "opportunity_contact_roles": {
        "report": "Opportunities with Contact Roles",
        "columns": {
            "opportunity_id": ("id", True, ["Opportunity ID"]),
            "contact_id": ("id", True, ["Contact ID"]),
            "role": ("text", False, ["Contact Role", "Role"]),
            "is_primary": ("bool", False, ["Primary", "Primary Contact"]),
        },
    },
    "campaign_members": {
        "report": "Campaigns with Campaign Members",
        "columns": {
            "campaign_id": ("id", True, ["Campaign ID"]),
            "lead_id": ("id", False, ["Lead ID"]),
            "contact_id": ("id", False, ["Contact ID"]),
            "status": ("text", True, ["Member Status", "Status"]),
            "is_responded": ("bool", True, ["Responded"]),
            "responded_date": ("date", False, ["First Responded Date", "Responded Date"]),
            "member_created_date": ("date", False, ["Member Created Date", "Member First Associated Date", "Date Added"]),
        },
    },
    "campaigns": {
        "report": "Campaigns",
        "columns": {
            "campaign_id": ("id", True, ["Campaign ID"]),
            "campaign_name": ("text", True, ["Campaign Name"]),
            "campaign_type": ("text", False, ["Type", "Campaign Type"]),
            "channel": ("text", False, ["Channel"]),
            "start_date": ("date", False, ["Start Date"]),
            "cost": ("money", False, ["Actual Cost", "Cost"]),
        },
    },
    "contacts": {
        "report": "Contacts & Accounts",
        "columns": {
            "contact_id": ("id", True, ["Contact ID"]),
            "account_id": ("id", True, ["Account ID"]),
            "full_name": ("text", False, ["Full Name", "Name", "Contact Name"]),
            "email": ("email", False, ["Email"]),
            "title": ("text", False, ["Title"]),
        },
    },
    "leads": {
        "report": "Leads",
        "columns": {
            "lead_id": ("id", True, ["Lead ID"]),
            "full_name": ("text", False, ["Full Name", "Name", "Lead Name"]),
            "company": ("text", False, ["Company / Account", "Company"]),
            "email": ("email", True, ["Email"]),
            "lead_source": ("text", True, ["Lead Source"]),
            "utm_source": ("text", False, ["UTM Source"]),
            "gclid": ("text", False, ["GCLID", "Google Click ID"]),
            "created_date": ("date", False, ["Created Date"]),
            "status": ("text", False, ["Lead Status", "Status"]),
            "is_converted": ("bool", True, ["Converted"]),
            "converted_contact_id": ("id", False, ["Converted Contact ID", "Converted Contact"]),
        },
    },
    "accounts": {
        "report": "Accounts",
        "columns": {
            "account_id": ("id", True, ["Account ID"]),
            "account_name": ("text", True, ["Account Name"]),
            "website_domain": ("domain", False, ["Website", "Website Domain"]),
        },
    },
}

# Which checks need an optional column. Used to explain what gets skipped.
OPTIONAL_NEEDS = {
    ("accounts", "website_domain"): "check 2 (unconverted leads at companies with open deals)",
    ("leads", "gclid"): "check 6 (paid search leads with no GCLID)",
    ("opportunities", "primary_campaign_id"): "sourced pipeline (everything shows as sales sourced)",
    ("campaign_members", "responded_date"): "the influence window and check 7",
    ("campaign_members", "member_created_date"): "dates for members who never responded (check 8 uses them)",
}

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M", "%m/%d/%y %I:%M %p"]


def _key(label):
    return re.sub(r"[^a-z0-9]", "", label.lower())


def clean(kind, raw):
    """Return (value, problem). Value is '' when blank."""
    v = (raw or "").strip()
    if v == "" or v == "-":
        return "", None
    if kind == "id":
        # 18-character Salesforce IDs = 15-character ID + 3-character suffix. Keep the 15 so files match.
        if len(v) == 18 and v.isalnum():
            v = v[:15]
        return v, None
    if kind == "bool":
        return ("Y" if v.lower() in ("y", "yes", "true", "1", "checked", "x") else "N"), None
    if kind == "date":
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d"), None
            except ValueError:
                pass
        return "", f"date not recognized: {v!r}"
    if kind == "money":
        num = re.sub(r"[^0-9.\-]", "", v)
        try:
            return float(num), None
        except ValueError:
            return "", f"amount not recognized: {v!r}"
    if kind == "email":
        return v.lower(), None
    if kind == "domain":
        d = re.sub(r"^https?://", "", v.lower())
        d = re.sub(r"^www\.", "", d).split("/")[0]
        return d, None
    return v, None


def read_folder(folder):
    """Read every expected CSV in a folder. Returns (tables, findings).

    tables: {file: list of row dicts using internal column names}
    findings: {file: {"found", "rows", "mapped", "missing_required", "missing_optional", "problems"}}
    """
    folder = Path(folder)
    tables, findings = {}, {}
    for name, spec in FILES.items():
        path = folder / f"{name}.csv"
        info = {"found": path.exists(), "rows": 0, "mapped": {}, "missing_required": [],
                "missing_optional": [], "problems": []}
        findings[name] = info
        if not path.exists():
            tables[name] = []
            continue
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames or []
            by_key = {_key(h): h for h in headers}
            for col, (kind, required, labels) in spec["columns"].items():
                src = next((by_key[_key(l)] for l in [col] + labels if _key(l) in by_key), None)
                if src:
                    info["mapped"][col] = src
                elif required:
                    info["missing_required"].append(col)
                else:
                    info["missing_optional"].append(col)
            rows = []
            for line_no, raw in enumerate(reader, start=2):
                # Salesforce report exports end with a few footer lines (report name, "Copyright..."). Skip them.
                filled = [v for v in raw.values() if isinstance(v, str) and v.strip()]
                if not filled or (len(filled) == 1 and len(headers) > 2):
                    continue
                first_src = info["mapped"].get(next(iter(spec["columns"])))
                if first_src and not (raw.get(first_src) or "").strip():
                    continue
                row = {}
                for col, (kind, _req, _labels) in spec["columns"].items():
                    src = info["mapped"].get(col)
                    value, problem = clean(kind, raw.get(src) if src else "")
                    row[col] = value
                    if problem:
                        info["problems"].append(f"line {line_no}, {src}: {problem}")
                rows.append(row)
            info["rows"] = len(rows)
            tables[name] = rows
    _resolve_primary_campaign(tables, findings)
    return tables, findings


def _resolve_primary_campaign(tables, findings):
    """Primary Campaign Source often exports as the campaign name. Swap names for IDs."""
    by_id = {c["campaign_id"] for c in tables["campaigns"]}
    by_name = {c["campaign_name"].lower(): c["campaign_id"] for c in tables["campaigns"]}
    for opp in tables["opportunities"]:
        v = opp.get("primary_campaign_id", "")
        if not v or v in by_id:
            continue
        if v.lower() in by_name:
            opp["primary_campaign_id"] = by_name[v.lower()]
        else:
            findings["opportunities"]["problems"].append(
                f"{opp['opportunity_id']}: primary campaign {v!r} is not in campaigns.csv")


def to_sqlite(tables, window_days=180):
    db = sqlite3.connect(":memory:")
    for name, spec in FILES.items():
        cols = list(spec["columns"])
        types = ["REAL" if spec["columns"][c][0] == "money" else "TEXT" for c in cols]
        db.execute(f"CREATE TABLE {name} ({', '.join(f'{c} {t}' for c, t in zip(cols, types))})")
        db.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})",
                       [[None if r[c] == "" else r[c] for c in cols] for r in tables[name]])
    db.execute("CREATE TABLE settings (influence_window_days INTEGER)")
    db.execute("INSERT INTO settings VALUES (?)", (window_days,))
    return db


def ready(findings):
    """True when every file is present with its required columns."""
    return all(f["found"] and not f["missing_required"] for f in findings.values())
