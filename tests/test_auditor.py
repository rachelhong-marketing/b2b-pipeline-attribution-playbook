import csv
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from auditor import load, checks, cli

DATA = Path(__file__).resolve().parent.parent / "data"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def run(folder, window=180):
    tables, findings = load.read_folder(folder)
    db = load.to_sqlite(tables, window)
    checks.prepare(db)
    return db, findings, {r["id"]: r for r in checks.run_checks(db, findings)}


def ids(rows, key):
    return sorted(r[key] for r in rows)


class SampleData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db, cls.findings, cls.results = run(DATA)

    def test_files_ready(self):
        self.assertTrue(load.ready(self.findings))

    def test_headline(self):
        h = checks.headline(self.db)
        self.assertEqual(h["pipeline"], 420000)
        self.assertAlmostEqual(h["sourced_pct"], 83.3, places=1)
        self.assertAlmostEqual(h["influenced_deal_pct"], 66.7, places=1)

    def test_checks_find_planted_problems(self):
        r = self.results
        self.assertEqual(ids(r[1]["rows"], "opportunity_id"), ["O03", "O06"])
        self.assertEqual(ids(r[2]["rows"], "lead_id"), ["L11", "L12", "L14"])
        self.assertEqual(ids(r[3]["rows"], "contact_id"), ["K05"])
        self.assertEqual(ids(r[4]["rows"], "lead_id"), ["L08", "L15"])
        self.assertEqual(r[5]["rows"][0]["email"], "maya@northwindretail.example")
        self.assertEqual(ids(r[6]["rows"], "lead_id"), ["L11"])
        self.assertEqual(r[7]["status"], "INFO")

    def test_inflation_check(self):
        email = next(x for x in self.results[8]["rows"] if x["campaign"] == "2026-Q1-Email-Nurture")
        self.assertEqual(email["pipeline_all_members"], 320000)
        self.assertEqual(email["pipeline_responded"], 150000)

    def test_shorter_window_drops_touches(self):
        _, _, short = run(DATA, window=30)
        self.assertGreater(len(short[7]["rows"]), len(self.results[7]["rows"]))


# Salesforce report labels for the columns in data/, used to fake a real export.
SF_LABELS = {
    "opportunities": {"opportunity_id": "Opportunity ID", "account_id": "Account ID", "opportunity_name": "Opportunity Name",
                      "amount": "Amount", "stage": "Stage", "is_closed": "Closed", "is_won": "Won",
                      "created_date": "Created Date", "close_date": "Close Date", "primary_campaign_id": "Primary Campaign Source"},
    "campaign_members": {"campaign_id": "Campaign ID", "lead_id": "Lead ID", "contact_id": "Contact ID",
                         "status": "Member Status", "is_responded": "Responded", "responded_date": "First Responded Date"},
    "leads": {"lead_id": "Lead ID", "full_name": "Full Name", "company": "Company / Account", "email": "Email",
              "lead_source": "Lead Source", "gclid": "GCLID", "created_date": "Created Date",
              "is_converted": "Converted", "converted_contact_id": "Converted Contact ID"},
    "accounts": {"account_id": "Account ID", "account_name": "Account Name", "website_domain": "Website"},
}


def salesforce_style_copy(dest):
    """Rewrite the sample data the way a Salesforce report export looks."""
    campaign_names = {r["campaign_id"]: r["campaign_name"] for r in read_csv(DATA / "campaigns.csv")}
    for src in DATA.glob("*.csv"):
        name = src.stem
        rows = read_csv(src)
        labels = SF_LABELS.get(name, {})
        out_cols = [labels.get(c, c) for c in rows[0].keys() if c in labels or not labels]
        keep = [c for c in rows[0].keys() if c in labels or not labels]
        with open(Path(dest) / src.name, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(out_cols)
            for r in rows:
                vals = []
                for c in keep:
                    v = r[c]
                    if c.endswith("date") and v:
                        v = datetime.strptime(v, "%Y-%m-%d").strftime("%-m/%-d/%Y")
                    elif c == "amount":
                        v = f"${float(v):,.2f}"
                    elif c.startswith("is_"):
                        v = {"Y": "1", "N": "0"}.get(v, v)
                    elif c == "primary_campaign_id" and v:
                        v = campaign_names[v]
                    elif c == "website_domain":
                        v = f"https://www.{v}/"
                    vals.append(v)
                w.writerow(vals)
            # Salesforce adds footer lines under the data.
            w.writerow([])
            w.writerow(['"Report name"'] + [""] * (len(out_cols) - 1))
            w.writerow(["Copyright (c) 2000-2026 example, inc. All rights reserved."] + [""] * (len(out_cols) - 1))


class SalesforceStyleExport(unittest.TestCase):
    def test_same_results_as_clean_data(self):
        tmp = tempfile.mkdtemp()
        try:
            salesforce_style_copy(tmp)
            db, findings, results = run(tmp)
            self.assertTrue(load.ready(findings), findings)
            self.assertEqual(findings["opportunities"]["rows"], 6)
            self.assertEqual(findings["opportunities"]["problems"], [])
            h = checks.headline(db)
            self.assertEqual(h["pipeline"], 420000)
            self.assertAlmostEqual(h["sourced_pct"], 83.3, places=1)
            self.assertEqual(ids(results[1]["rows"], "opportunity_id"), ["O03", "O06"])
            self.assertEqual(ids(results[2]["rows"], "lead_id"), ["L11", "L12", "L14"])
        finally:
            shutil.rmtree(tmp)

    def test_missing_file_blocks_audit(self):
        tmp = tempfile.mkdtemp()
        try:
            for f in DATA.glob("*.csv"):
                if f.name != "opportunity_contact_roles.csv":
                    shutil.copy(f, tmp)
            with redirect_stdout(io.StringIO()) as out:
                code = cli.main(["audit", tmp])
            self.assertEqual(code, 1)
            self.assertIn("opportunity_contact_roles.csv: MISSING", out.getvalue())
        finally:
            shutil.rmtree(tmp)


class Cleaning(unittest.TestCase):
    def test_values(self):
        self.assertEqual(load.clean("id", "0065g00000AbCdEFGH")[0], "0065g00000AbCdE")
        self.assertEqual(load.clean("money", "USD 1,250.50")[0], 1250.5)
        self.assertEqual(load.clean("date", "3/7/2026 9:15 AM")[0], "2026-03-07")
        self.assertEqual(load.clean("bool", "true")[0], "Y")
        self.assertEqual(load.clean("domain", "http://www.acme.example/about")[0], "acme.example")
        self.assertIsNotNone(load.clean("date", "next Tuesday")[1])


if __name__ == "__main__":
    unittest.main()
