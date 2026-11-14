# Monthly attribution audit

Run the queries in `sql/03_data_audit.sql`, or build the same checks as CRM reports. Log anything you find in `discrepancy-log.csv`.

| Check | Count this month | Count last month | Owner | Action |
|---|---|---|---|---|
| Influenced pipeline: all members vs. responded only (gap) | | | Marketing Ops | |
| Opportunities with no contact roles | | | Sales Ops | |
| Unconverted leads at accounts with open deals | | | Sales development | |
| Engaged contacts not on their account's open deal | | | Sales | |
| Leads with no lead source | | | Marketing Ops | |
| Duplicate leads or contacts | | | Marketing Ops | |
| Campaigns with no cost entered | | | Campaign owners | |
| Paid leads with no UTM or click ID | | | Marketing Ops, web | |
| Offline lists uploaded without a campaign | | | Event and partner owners | |

**Trend to watch:** if a count goes up two months in a row, fix the process causing it (the form, sync or rule), not just the records.
