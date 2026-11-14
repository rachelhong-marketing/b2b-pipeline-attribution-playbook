"""Pipeline numbers and the 8 data checks. Same logic as sql/01-03, run in Python's built-in SQLite."""

INFLUENCE_LINKS = """
CREATE VIEW influence_links AS
SELECT o.opportunity_id, o.opportunity_name, o.amount, o.created_date AS opp_created_date,
       cm.campaign_id, c.campaign_name, cm.contact_id, cm.status, cm.responded_date
FROM opportunities o
JOIN opportunity_contact_roles ocr ON ocr.opportunity_id = o.opportunity_id
JOIN campaign_members cm           ON cm.contact_id = ocr.contact_id
JOIN campaigns c                   ON c.campaign_id = cm.campaign_id
CROSS JOIN settings s
WHERE cm.is_responded = 'Y'
  AND julianday(cm.responded_date) <= julianday(o.created_date)
  AND julianday(o.created_date) - julianday(cm.responded_date) <= s.influence_window_days
"""

# Every member on a deal's contacts, responded or not (e.g. email "Sent"). Used by check 8.
ALL_MEMBER_LINKS = """
CREATE VIEW all_member_links AS
SELECT DISTINCT o.opportunity_id, cm.campaign_id, o.amount
FROM opportunities o
JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
JOIN campaign_members cm         ON cm.contact_id = r.contact_id
CROSS JOIN settings s
WHERE julianday(COALESCE(cm.responded_date, cm.member_created_date)) <= julianday(o.created_date)
  AND julianday(o.created_date) - julianday(COALESCE(cm.responded_date, cm.member_created_date)) <= s.influence_window_days
"""


def prepare(db):
    db.execute(INFLUENCE_LINKS)
    db.execute(ALL_MEMBER_LINKS)


def _rows(db, sql, *args):
    cur = db.execute(sql, args)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def headline(db):
    r = _rows(db, """
        SELECT COUNT(*) AS deals,
               COALESCE(SUM(amount), 0) AS pipeline,
               COALESCE(SUM(CASE WHEN primary_campaign_id IS NOT NULL THEN amount END), 0) AS sourced
        FROM opportunities""")[0]
    influenced = _rows(db, """
        SELECT COUNT(*) AS deals, COALESCE(SUM(amount), 0) AS pipeline
        FROM (SELECT DISTINCT opportunity_id, amount FROM influence_links)""")[0]
    r["sourced_pct"] = 100.0 * r["sourced"] / r["pipeline"] if r["pipeline"] else 0.0
    r["influenced_deals"] = influenced["deals"]
    r["influenced_pipeline"] = influenced["pipeline"]
    r["influenced_deal_pct"] = 100.0 * influenced["deals"] / r["deals"] if r["deals"] else 0.0
    return r


def sourced_by_campaign(db):
    return _rows(db, """
        SELECT COALESCE(c.campaign_name, '(none: sales sourced)') AS campaign,
               COUNT(*) AS deals, SUM(o.amount) AS pipeline
        FROM opportunities o LEFT JOIN campaigns c ON c.campaign_id = o.primary_campaign_id
        GROUP BY campaign ORDER BY pipeline DESC""")


def influenced_by_campaign(db):
    return _rows(db, """
        SELECT campaign_name AS campaign, COUNT(*) AS deals, SUM(amount) AS pipeline
        FROM (SELECT DISTINCT opportunity_id, campaign_name, amount FROM influence_links)
        GROUP BY campaign_name ORDER BY pipeline DESC""")


def attribution_models(db):
    return _rows(db, """
        WITH ranked AS (
          SELECT campaign_name, amount,
                 ROW_NUMBER() OVER (PARTITION BY opportunity_id ORDER BY responded_date ASC,  campaign_id) AS first_rank,
                 ROW_NUMBER() OVER (PARTITION BY opportunity_id ORDER BY responded_date DESC, campaign_id) AS last_rank,
                 COUNT(*)     OVER (PARTITION BY opportunity_id) AS touches
          FROM influence_links)
        SELECT campaign_name AS campaign,
               SUM(CASE WHEN first_rank = 1 THEN amount ELSE 0 END) AS first_touch,
               SUM(CASE WHEN last_rank  = 1 THEN amount ELSE 0 END) AS last_touch,
               ROUND(SUM(amount * 1.0 / touches), 0) AS even_split
        FROM ranked GROUP BY campaign_name ORDER BY even_split DESC""")


CHECKS = [
    {
        "id": 1, "name": "Deals with no contact roles",
        "why": "Campaign influence can't link to a deal with no contact roles, so marketing gets no credit for it.",
        "fix": "Add contact roles (backfill past deals); require them before a deal can move to a later stage.",
        "doc": "docs/04-contact-roles.md",
        "sql": """
            SELECT o.opportunity_id, o.opportunity_name, o.stage, o.amount
            FROM opportunities o
            LEFT JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
            WHERE r.opportunity_id IS NULL ORDER BY o.amount DESC""",
        "at_risk": "amount",
    },
    {
        "id": 2, "name": "Unconverted leads at companies with open deals",
        "why": "Their campaign touches stay on the lead and never reach the deal.",
        "fix": "Convert them to contacts on the matching account, then add them to the deal with a contact role.",
        "doc": "docs/03-convert-and-match.md",
        "needs": ("accounts", "website_domain"),
        "sql": """
            SELECT l.lead_id, l.full_name, l.company, l.status, o.opportunity_name, o.amount
            FROM leads l
            JOIN accounts a      ON a.website_domain = substr(l.email, instr(l.email, '@') + 1)
            JOIN opportunities o ON o.account_id = a.account_id AND o.is_closed = 'N'
            WHERE l.is_converted = 'N' ORDER BY o.amount DESC""",
        "at_risk": "deal",
    },
    {
        "id": 3, "name": "Engaged contacts missing from their account's open deal",
        "why": "They engaged with campaigns, but with no contact role their touches don't count on the deal.",
        "fix": "Ask the deal owner whether they're part of the buying group; if so, add a contact role.",
        "doc": "docs/04-contact-roles.md",
        "sql": """
            SELECT DISTINCT k.contact_id, k.full_name, a.account_name, o.opportunity_name, o.amount
            FROM contacts k
            JOIN accounts a          ON a.account_id = k.account_id
            JOIN opportunities o     ON o.account_id = k.account_id AND o.is_closed = 'N'
            JOIN campaign_members cm ON cm.contact_id = k.contact_id AND cm.is_responded = 'Y'
            LEFT JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id AND r.contact_id = k.contact_id
            WHERE r.contact_id IS NULL""",
        "at_risk": "deal",
    },
    {
        "id": 4, "name": "Leads with no lead source",
        "why": "Source reports can't place them, so they fall into 'unknown'.",
        "fix": "Make lead source required on every form and import; fill past gaps from UTMs or the first campaign.",
        "doc": "docs/02-capture-the-source.md",
        "sql": """
            SELECT lead_id, full_name, company, created_date
            FROM leads WHERE lead_source IS NULL""",
    },
    {
        "id": 5, "name": "Possible duplicate leads (same email)",
        "why": "Touches split across two records, and one of them may never convert.",
        "fix": "Merge the duplicates and turn on a duplicate rule for leads.",
        "doc": "docs/03-convert-and-match.md",
        "sql": """
            SELECT email, COUNT(*) AS records, GROUP_CONCAT(lead_id) AS lead_ids
            FROM leads WHERE email IS NOT NULL
            GROUP BY email HAVING COUNT(*) > 1""",
    },
    {
        "id": 6, "name": "Paid search leads with no GCLID",
        "why": "Without the Google click ID, Google Ads can't learn which clicks became pipeline.",
        "fix": "Capture the GCLID in a hidden form field and map it to the lead.",
        "doc": "docs/08-close-the-loop.md",
        "needs": ("leads", "gclid"),
        "sql": """
            SELECT lead_id, full_name, lead_source, created_date
            FROM leads WHERE lead_source = 'Paid Search' AND gclid IS NULL""",
    },
    {
        "id": 7, "name": "Touches outside the influence window",
        "why": "These responses happened too long before the deal was created to count. That may be right, or the window may be too short for your sales cycle.",
        "fix": "No record fix needed. Check that the window matches your sales cycle.",
        "doc": "docs/05-sourced-vs-influenced.md",
        "needs": ("campaign_members", "responded_date"),
        "sql": """
            SELECT o.opportunity_name, cm.campaign_id, cm.contact_id, cm.responded_date, o.created_date AS deal_created
            FROM opportunities o
            JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
            JOIN campaign_members cm         ON cm.contact_id = r.contact_id AND cm.is_responded = 'Y'
            CROSS JOIN settings s
            WHERE julianday(o.created_date) - julianday(cm.responded_date) > s.influence_window_days""",
        "info_only": True,
    },
    {
        "id": 8, "name": "Influence inflated by members who never engaged",
        "why": "If statuses like 'Sent' or 'Received' count as responses, the Campaign Influence report credits a campaign on deals where nobody engaged.",
        "fix": "Mark only real engagement statuses (clicked, attended, downloaded) as Responded, and report influence on responded members only.",
        "doc": "docs/07-reconcile-and-audit.md",
        "sql": """
            SELECT c.campaign_name AS campaign,
                   (SELECT COUNT(*) FROM all_member_links a WHERE a.campaign_id = c.campaign_id) AS deals_all_members,
                   (SELECT COALESCE(SUM(amount), 0) FROM all_member_links a WHERE a.campaign_id = c.campaign_id) AS pipeline_all_members,
                   (SELECT COUNT(*) FROM (SELECT DISTINCT opportunity_id, campaign_id FROM influence_links) i
                     WHERE i.campaign_id = c.campaign_id) AS deals_responded,
                   (SELECT COALESCE(SUM(amount), 0) FROM (SELECT DISTINCT opportunity_id, campaign_id, amount FROM influence_links) i
                     WHERE i.campaign_id = c.campaign_id) AS pipeline_responded
            FROM campaigns c""",
    },
]


def run_checks(db, findings):
    """Run each check. Returns a list of results with rows, status and pipeline at risk."""
    results = []
    for chk in CHECKS:
        needs = chk.get("needs")
        if needs and needs[1] in findings[needs[0]]["missing_optional"]:
            results.append({**chk, "status": "SKIPPED", "rows": [], "at_risk_amount": 0,
                            "skipped_because": f"{needs[0]}.csv has no {needs[1]} column"})
            continue
        rows = _rows(db, chk["sql"])
        if chk["id"] == 8:
            rows = [r for r in rows if r["pipeline_all_members"] > r["pipeline_responded"]]
            rows.sort(key=lambda r: r["pipeline_responded"] - r["pipeline_all_members"])
        at_risk = 0
        if chk.get("at_risk") == "amount":
            at_risk = sum(r["amount"] or 0 for r in rows)
        elif chk.get("at_risk") == "deal":
            seen = {}
            for r in rows:
                seen[r["opportunity_name"]] = r["amount"] or 0
            at_risk = sum(seen.values())
        elif chk["id"] == 8:
            at_risk = sum(r["pipeline_all_members"] - r["pipeline_responded"] for r in rows)
        if not rows:
            status = "OK"
        else:
            status = "INFO" if chk.get("info_only") else "FIX"
        results.append({**chk, "status": status, "rows": rows, "at_risk_amount": at_risk})
    return results
