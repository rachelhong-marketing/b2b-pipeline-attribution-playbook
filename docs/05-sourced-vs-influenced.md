# Part 5: Sourced vs. influenced pipeline

These are the two numbers leadership asks for most. They answer different questions, so report both.

| | Sourced pipeline | Influenced pipeline |
|---|---|---|
| **Question** | Did marketing start this deal? | Did marketing touch this deal before it was created? |
| **Credit** | One campaign gets 100% of the deal | Every campaign a buyer on the deal engaged with is linked to it |
| **Salesforce field or report** | **Primary Campaign Source** on the opportunity | **Campaign Influence** (needs contact roles) |
| **Adds up to total pipeline?** | Yes, each deal counts once | No. One deal can be influenced by many campaigns, so don't add influenced totals across campaigns |
| **Good for** | "How much pipeline did marketing create?" | "Which campaigns help deals move forward?" |

## Sourced pipeline: Primary Campaign Source

- Each opportunity has one **Primary Campaign Source** field that points to one campaign.
- How it gets filled in depends on your org's setup. It can be set automatically when a lead converts to a deal, by a flow, or by hand. Some orgs set it to the most recent campaign and some to the first. **Check how yours works before reporting on it.**
- Many teams define "marketing sourced" as: the deal's primary campaign is a marketing campaign, or the primary contact's original lead source is a marketing channel. Pick one rule, write it down and use it every time.
- Deals with no primary campaign are usually counted as sales sourced.

## Influenced pipeline: Campaign Influence

Campaign Influence links a deal to the campaigns its buyers engaged with. Salesforce's default setup adds a campaign to an opportunity automatically when:
1. A contact on the opportunity has a **contact role** (see [Part 4](04-contact-roles.md)).
2. That contact is a **member of the campaign**.
3. They joined the campaign within a set **time window** before the deal was created (an admin sets the number of days).

With **Customizable Campaign Influence**, you can also split the deal amount across those campaigns using a model, like even split, or your own rules (see [Part 6](06-attribution-models-and-tools.md)).

### Settings to agree on
- **Time window:** how far back a touch can count. 90 or 180 days before the deal is created is common for longer sales cycles. Too long and old touches get credit. Too short and early touches are lost.
- **Touches after the deal is created:** some teams count touches up to close, since marketing often supports open deals. Decide and document it.
- **Which statuses count:** only real engagement (clicked, attended, downloaded), not "sent," "received" or "registered." This is the setting most likely to inflate influenced pipeline. If everyone on an email list counts, one big send can show up on most of your deals. See [Part 7](07-reconcile-and-audit.md#dont-take-the-campaign-influence-report-at-face-value).

## Example from the sample data

In this repo's sample data (all made up):
- The Cedar Foods deal has no primary campaign, so it's **sales sourced**. But its buyer downloaded a guide and clicked a nurture email before the deal was created, so it's **marketing influenced**.
- The Summit Travel deal is sourced by a LinkedIn campaign, but has **no contact roles**, so no campaign shows as influencing it. That's a data gap, not a lack of marketing.

Run [sql/01_sourced_vs_influenced.sql](../sql/01_sourced_vs_influenced.sql) to see both views side by side.

## How to report it

- Report **sourced pipeline** as a share of total pipeline: "Marketing sourced X% of new pipeline this quarter."
- Report **influenced pipeline** as a share of deals touched: "Marketing touched X% of open deals." Don't add influenced amounts across campaigns.
- Show both by channel, so you can see channels that start deals (like paid search) and channels that help close them (like events and webinars).

## Sources
- [Salesforce Ben: Campaign Influence, a marketer's guide](https://www.salesforceben.com/salesforce-campaign-influence-marketers-guide/)
- [How Customizable Campaign Influence works (Tectonic)](https://gettectonic.com/customizable-campaign-influence/)
- [Salesforce Campaign Influence explained (LeadJourney)](https://leadjourney.io/blog/salesforce-campaign-influence-explained)
- [Customize Primary Campaign Source with Salesforce Flow](https://thespotforpardot.com/?p=7423)
