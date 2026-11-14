# Part 7: Reconcile and audit the data

Ad platforms, the marketing automation tool and the CRM will never show the same numbers. That's normal, because each one counts something different. The goal isn't to make them match. It's to explain the gaps and agree which system owns which metric.

## Why the numbers differ

| System | What it counts | Why it's different |
|---|---|---|
| **Ad platforms** (Google Ads, LinkedIn) | Conversions | Counts repeat form fills; uses its own attribution window; may count view-through conversions; counts by click date or conversion date |
| **Marketing automation** (HubSpot, Eloqua, Account Engagement) | People and their activity | Removes duplicates, filters spam and bots, merges records; scoring changes over time |
| **CRM** (Salesforce) | Leads, contacts, opportunities | Uses its own date fields (created date, MQL date, close date); records get merged, converted or deleted during routing |

**Common breaks between them:**
- UTMs or GCLIDs not saved to the record, or overwritten later
- Sync delays, or fields not mapped from the marketing automation tool to the CRM
- Cookie consent or browser privacy settings blocking tracking
- Leads uploaded by hand (events, partners) with no campaign or source
- Different time zones or reporting periods
- Test, internal and spam submissions not removed

## Don't take the Campaign Influence report at face value

The Campaign Influence report is the easiest place to inflate pipeline without meaning to. Depending on how it's set up, it can count **every campaign member** on a deal's contacts, not just people who engaged.

**The most common example is email.** An email campaign often adds everyone on the send list as a member with a status like "Sent" or "Received." If those statuses count, every deal whose buyers were on the list shows as "influenced" by that email, even if nobody opened it. The same happens with webinar registrants who never attended, or event invitees who never showed up.

The result: one large email send can make a campaign look like it influenced most of the pipeline. Leadership sees a big number, and marketing loses credibility when sales asks what the email actually did.

**How to keep it honest:**
- **Decide which statuses count as engagement,** such as Clicked, Downloaded, Attended or Visited booth, and mark only those as "Responded" on every campaign.
- **Filter influence reports to responded members only,** or set the influence rules to only link responded members, if your setup allows it.
- **Separate broad sends from real engagement.** Report email sends, ad impressions and invites as reach, not influence.
- **Check before you present.** Compare the influenced pipeline with all members vs. responded members only. A big gap means the report is overstating marketing's impact.
- **Explain the rule in the report itself,** for example: "Influenced = a buyer on the deal clicked, downloaded, attended or visited, within 180 days before the deal was created."

[sql/03_data_audit.sql](../sql/03_data_audit.sql) (check 8) runs this comparison on the sample data. The email nurture campaign shows $320K of influenced pipeline when every member counts, and $150K when only people who clicked count. The rest came from contacts who were only sent or received the email.

## A step-by-step method

1. **Pick one time frame and one date field** for every system, such as "leads created Jan 1–Mar 31."
2. **Line up the counts** from each system in one table: platform conversions, marketing automation leads, CRM leads, MQLs.
3. **Explain each gap, one cause at a time.** Start with the biggest. Remove duplicates, then spam, then records with no source, and so on.
4. **Log each gap** with its cause, the fix and the team that owns the fix. Use [templates/discrepancy-log.csv](../templates/discrepancy-log.csv).
5. **Agree on a source of truth for each metric**, for example:
   - Spend, impressions and clicks: the ad platform
   - Leads and engagement: the marketing automation tool
   - MQLs, pipeline and revenue: the CRM
6. **Fix the process, not just the report.** Most gaps come back next quarter unless the form, sync or rule causing them is fixed.

## Worked example (made-up numbers)

A paid social campaign for one quarter:

| Step | Count | Gap explained |
|---|---|---|
| Conversions in the ad platform | 120 | |
| Leads in the marketing automation tool | 95 | 15 repeat form fills by the same people; 10 spam or test submissions removed |
| Leads in the CRM with this campaign | 80 | 9 leads synced without the campaign (UTM field not mapped); 6 merged into existing contacts during routing |
| MQLs | 30 | Expected. Not every lead qualifies |

Once the gaps are explained, the fixes are clear: map the UTM field, and make sure merged records keep their campaign membership.

## Monthly data audit

Run these checks every month. The queries are in [sql/03_data_audit.sql](../sql/03_data_audit.sql), and the checklist is in [templates/monthly-audit-checklist.md](../templates/monthly-audit-checklist.md).

| Check | Why it matters | Usually owned by |
|---|---|---|
| Campaigns where "Sent," "Received" or "Registered" count as a response | Inflates influenced pipeline | Marketing Ops, campaign owners |
| Opportunities with no contact roles | Campaign influence can't link to them | Sales Ops |
| Unconverted leads at accounts with open deals | Their touches never reach the deal | Sales development, Sales Ops |
| Leads with no lead source | Can't be counted as marketing or sales sourced | Marketing Ops |
| Duplicate leads or contacts | Touches split across records | Marketing Ops |
| Campaigns with no cost | Can't calculate cost per MQL | Campaign owners |
| Leads from paid clicks with no UTM or GCLID saved | Ad results can't be tied to pipeline | Marketing Ops, web team |

## Key formulas

| Metric | Formula |
|---|---|
| Lead-to-MQL rate | MQLs ÷ leads |
| Cost per lead | Campaign cost ÷ leads |
| Cost per MQL | Campaign cost ÷ MQLs |
| % of leads from target accounts | Leads at target accounts ÷ all leads |
| Sourced pipeline share | Marketing-sourced pipeline ÷ total new pipeline |
| Influenced deal share | Deals with at least one marketing touch ÷ all deals |

Spreadsheet versions are in [templates/spreadsheet-formulas.md](../templates/spreadsheet-formulas.md).
