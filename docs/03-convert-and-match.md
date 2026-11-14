# Part 3: Convert the lead and match the account

In Salesforce, a **lead** is a person who isn't tied to a company record yet. Opportunities live on **accounts** and include **contacts**. To get credit for a deal, a lead's history has to move onto a contact on the right account.

## What conversion does

When a lead is converted, Salesforce:
- Creates a **contact** (or merges into an existing one).
- Links it to an **account** (existing or new).
- Can create an **opportunity** at the same time.
- Moves the person's **campaign memberships** to the contact, so their past touches are kept. If the person was already a member of the same campaign as both a lead and a contact, check for duplicate memberships.

If a lead is never converted, its campaign touches stay on the lead. They can't show up on any opportunity, even if the person's company is in a deal.

## Where it breaks

| Problem | What happens | Fix |
|---|---|---|
| Lead never converted | Their webinar, ad click and download never reach the deal | Convert leads when they become SQLs, or when they're working with sales on an open deal |
| Converted to a new account instead of the existing one | Two accounts for the same company; the deal is on one, the touches on the other | Use lead-to-account matching (a matching tool or rule) before conversion |
| Duplicate contact created | Touches split across two contact records | Turn on duplicate rules; merge duplicates monthly |
| Lead converted without creating an opportunity, and the deal is created later | Fine, as long as the contact is added to the deal with a contact role (see [Part 4](04-contact-roles.md)) | Make adding contact roles part of opening a deal |

## Lead-to-account matching

Most B2B companies have many people from one company engaging over time. Before converting, check whether the account already exists:
- Match on company website domain first, then company name.
- Many teams use a matching tool or a CRM rule to route new leads to the account owner automatically.
- If your sales team works by account, consider showing unconverted leads on the account page so reps can see engaged people and convert them.

## Before you move on

- [ ] There's a clear rule for when leads get converted (for example, at SQL).
- [ ] Leads are matched to existing accounts by domain before conversion.
- [ ] Duplicate rules are on, and duplicates are merged on a schedule.
- [ ] A monthly check finds unconverted leads at accounts with open deals (see the audit query in [sql/03_data_audit.sql](../sql/03_data_audit.sql)).

## Sources
- [Salesforce Help: Convert leads](https://help.salesforce.com/HTViewHelpDoc?id=leads_convert.htm)
- [Lead-to-account matching in Salesforce: what breaks and how to fix it (Leadspace)](https://leadspace.com/resources/lead-to-account-matching-in-salesforce-what-breaks-and-how-to-fix-it)
- [Salesforce Admins: Deal with duplicates](https://admin.salesforce.com/deal-duplicates-two-tactics-use-today)
