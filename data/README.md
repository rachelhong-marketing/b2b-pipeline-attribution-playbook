# Sample data (made up)

**Everything in this folder is fake.** The companies, people, emails, campaigns, dates and dollar amounts were invented to show how the attribution chain works. They don't come from any real company, CRM or client.

- Company names are fictional, and email domains end in `.example`, a domain reserved for examples.
- Amounts are round numbers chosen to make the math easy to follow.
- Data problems were added on purpose, so the audit queries have something to find. See [sql/README.md](../sql/README.md) for the list.

| File | What it holds |
|---|---|
| `accounts.csv` | 6 fictional companies, with a target account flag |
| `leads.csv` | 15 leads: converted, unconverted, a duplicate and some with no lead source |
| `contacts.csv` | 10 contacts created from converted leads |
| `campaigns.csv` | 7 campaigns with type, channel, start date and cost |
| `campaign_members.csv` | Campaign touches with status, whether it counts as a response, and date |
| `opportunities.csv` | 6 deals with amount, stage, dates and primary campaign |
| `opportunity_contact_roles.csv` | Which contacts are on which deal, and their role |
