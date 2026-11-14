# Run the queries

You only need SQLite, which comes with macOS and most Linux systems. From the repo root:

```bash
sqlite3 attribution.db < sql/00_load_data.sql
sqlite3 -header -column attribution.db < sql/01_sourced_vs_influenced.sql
sqlite3 -header -column attribution.db < sql/02_attribution_models.sql
sqlite3 -header -column attribution.db < sql/03_data_audit.sql
```

To start over, delete `attribution.db` and load again.

| File | What it shows | Part |
|---|---|---|
| `00_load_data.sql` | Loads the CSVs, sets the influence window (180 days) and builds the `influence_links` view | 5 |
| `01_sourced_vs_influenced.sql` | Sourced pipeline by primary campaign, influenced pipeline by campaign, a deal-by-deal view and headline numbers | 5 |
| `02_attribution_models.sql` | The same deals under first touch, last touch and even split | 6 |
| `03_data_audit.sql` | Eight checks: records that break the chain, plus an influence inflation check | 7 |

## What to look for in the sample data

All names and numbers are made up (see [data/README.md](../data/README.md)). The data has these problems on purpose:
- **Summit Travel** is a won deal sourced by LinkedIn, but has no contact roles, so no campaign shows as influencing it.
- **Cedar Foods** is sales sourced (no primary campaign), but its buyer engaged with two marketing campaigns before the deal was created.
- **Sam Ortiz** (Bluebird Bank), **Kim Tran** (Pine Auto) and **Rita Moss** (Harbor Health) are MQLs who were never converted, at companies with open deals.
- **Priya Shah** engaged with a nurture email but isn't a contact role on Bluebird Bank's open deal.
- **Maya Lin** has a duplicate lead record.
- Several contacts were only **sent or received** the Q1 email nurture. Check 8 in `03_data_audit.sql` shows how much they would inflate influenced pipeline if they counted.
- A Pine Auto touch from 2025 falls outside the 180-day window, and one Pine Auto touch happened after the deal was created. Neither counts as influence with these settings.

Try changing `influence_window_days` in `00_load_data.sql`, or adding the missing contact roles, then rerun the queries to see how the numbers change.

## Using this with your own CRM

Table and field names follow Salesforce objects (Lead, Contact, Account, Campaign, CampaignMember, Opportunity, OpportunityContactRole), simplified. The date functions are SQLite. For other databases, swap `julianday()` for your date difference function.
