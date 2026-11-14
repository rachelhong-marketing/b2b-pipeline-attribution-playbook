# Export your Salesforce reports for the audit

The auditor needs 7 CSV files in one folder. Each one is a standard Salesforce report exported as CSV. Building them takes about 20 minutes the first time. Save the reports in a folder so next month you only re-export.

## How to export each report

1. Build the report with the report type and columns below. Remove any default filters that hide records (for example, "My opportunities" or "Current FY"). Use **All** records and a date range that covers your audit period plus the influence window (for example, the last 12 to 18 months).
2. Click **Export**, choose **Details Only**, and pick **Comma Delimited .csv**.
3. Rename the file to the name in the table and save it in your audit folder (for example, `exports/2026-11/`).

You don't need to rename columns. The auditor reads the usual Salesforce labels ("Opportunity ID", "Primary Campaign Source", "First Responded Date" and so on). It also handles US-style dates, dollar signs, true/false checkboxes, 18-character IDs and the footer lines Salesforce adds under the data.

## The 7 reports

**Required** columns must be there or the audit stops. **Optional** columns turn on extra checks.

### 1. `opportunities.csv`: report type **Opportunities**
- Required: Opportunity ID, Account ID, Opportunity Name, Amount, Stage, Closed, Created Date
- Optional: Won, Close Date, **Primary Campaign Source** (without it, every deal shows as sales sourced)

### 2. `opportunity_contact_roles.csv`: report type **Opportunities with Contact Roles**
- Required: Opportunity ID, Contact ID
- Optional: Contact Role, Primary

### 3. `campaign_members.csv`: report type **Campaigns with Campaign Members**
- Required: Campaign ID, Member Status, Responded
- Include both: Lead ID and Contact ID (a member is one or the other)
- Optional: **First Responded Date** (needed for the influence window), and the date the person was added to the campaign. Its label varies by org; if the auditor doesn't pick it up, rename that column to `member_created_date`. Check 8 uses it to date members who never responded.
- Include **all** member statuses, including "Sent" and "Received." Check 8 needs them to measure inflation.

### 4. `campaigns.csv`: report type **Campaigns**
- Required: Campaign ID, Campaign Name
- Optional: Type, Channel (often a custom field), Start Date, Actual Cost

### 5. `contacts.csv`: report type **Contacts & Accounts**
- Required: Contact ID, Account ID
- Optional: Full Name, Email, Title

### 6. `leads.csv`: report type **Leads**
- Required: Lead ID, Email, Lead Source, Converted
- Optional: Full Name, Company / Account, Created Date, Lead Status, Converted Contact ID, **GCLID** (a custom field in most orgs; needed for check 6), UTM Source
- Make sure converted leads aren't filtered out.

### 7. `accounts.csv`: report type **Accounts**
- Required: Account ID, Account Name
- Optional: **Website** (needed for check 2, which matches lead email domains to accounts)

## Field names that differ in your org

Custom fields (GCLID, Channel, UTMs) can have any label. If `check-files` says a column is missing but you have it under another name, rename the column header in the CSV to the name in brackets below and run it again:

`gclid`, `channel`, `utm_source`, `member_created_date`, `website_domain`, `primary_campaign_id`

## Check the folder before auditing

```bash
python3 -m auditor check-files exports/2026-11
```

It lists each file, row counts, any missing columns, which checks are skipped without them, and values it couldn't read (such as a date in an unexpected format).

## Keep the data private

These exports contain names and emails. The Python auditor runs entirely on your computer and sends nothing anywhere. If you use the Claude Code skill, the report is read by an AI assistant, so check your company's policy on using CRM data with AI tools first. Never commit exports to GitHub: the `exports/` folder is in `.gitignore`.
