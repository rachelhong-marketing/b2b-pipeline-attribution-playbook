# Part 4: Attach contacts with contact roles

B2B deals rarely come down to one person. A buyer might download a report, a technical lead might attend a webinar, and a VP might click a search ad. Each of them can be a campaign member. **Contact roles** are what connect those people to the deal.

## How it works

On each opportunity, add every buyer involved as a contact role, such as Decision Maker, Economic Buyer, Evaluator, Technical Buyer or Influencer. Mark one as primary.

Once a contact has a role on the opportunity, Salesforce can link the campaigns that person joined to the deal. This is what Campaign Influence reports are built on (see [Part 5](05-sourced-vs-influenced.md)).

**No contact role, no influence.** If a deal has no contact roles, every campaign those buyers engaged with is invisible on that deal.

## Why sales often skips it

- It's an extra step with no direct benefit to the rep.
- Some reps open opportunities late, close to signing, because an early deal that doesn't close hurts their win rate. By then, earlier buyers often aren't added.
- Reps add the one person they talk to most, not the whole buying group.

## How to fix it

**1. Backfill past deals**
Sales Ops can run a one-time automation that adds a contact role for the contacts on each opportunity's account. For example, add the contacts who engaged in the last 12 months. It's not perfect, but it gives the influence report history to work with.

**2. Make it part of the process going forward**
- **Stage rules:** a validation rule or flow that stops a deal from moving past a set stage, like proposal, without at least one contact role and an amount.
- **Automation:** when a deal is created from a converted lead, add that contact as the primary contact role automatically.
- **Prompts:** show reps which contacts at the account engaged recently, so adding them is one click.

**3. Get the right owner behind it**
Marketing asking sales to update records rarely works on its own. It works better when Sales Ops owns the rule and leadership uses the reports. In some companies, Sales Ops reports into Finance, which makes pipeline rules easier to enforce. That organizational point matters as much as the setup.

## Before you move on

- [ ] Past opportunities have contact roles backfilled.
- [ ] A stage rule requires contact roles before a deal moves forward.
- [ ] New opportunities created from lead conversion get a primary contact role automatically.
- [ ] A monthly check finds opportunities with no contact roles (see [sql/03_data_audit.sql](../sql/03_data_audit.sql)).

## Sources
- [Salesforce Ben: 4 ways to create contact roles for accurate campaign influence reporting](https://www.salesforceben.com/the-drip/4-ways-to-create-salesforce-contact-roles-and-get-accurate-campaign-influence-reporting/)
- [Salesforce Ben: Campaign Influence, a marketer's guide](https://www.salesforceben.com/salesforce-campaign-influence-marketers-guide/)
