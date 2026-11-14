# Part 6: Attribution models and tools

Once campaigns are linked to deals, you have to decide how to split the credit. No model is "right." Pick one that fits how your buyers decide, explain it, and stick with it long enough to compare quarters.

## Common models

| Model | How credit is split | Good for | Watch out for |
|---|---|---|---|
| **First touch** | 100% to the first campaign | Seeing what brings new people in | Ignores everything that moved the deal later |
| **Last touch** | 100% to the last campaign before the deal | Seeing what tips people into a conversation | Overcredits bottom-of-funnel tactics like demo requests |
| **Even split (linear)** | Shared equally across all linked campaigns | Simple, fair starting point for multi-touch | Treats a quick email click the same as an event meeting |
| **Position based** (U-shaped, W-shaped) | Larger shares to key moments, like first touch, lead creation and deal creation, with the rest spread out | Valuing the moments that matter most | Weights are a judgment call |
| **Time decay** | More credit to touches closer to the conversion | Shorter sales cycles | Undervalues early awareness work |

[sql/02_attribution_models.sql](../sql/02_attribution_models.sql) calculates first touch, last touch and even split on the sample data, so you can see how the same deals give each campaign different credit.

## In Salesforce

- **Campaign Influence 1.0 (classic):** the primary campaign gets credit, and other campaigns can be linked to the deal. It's mostly a sourced view.
- **Customizable Campaign Influence:** turn it on in Setup → Campaign Influence Settings.
  - Campaigns are linked to deals automatically through contact roles, campaign membership and a time window (see [Part 5](05-sourced-vs-influenced.md)).
  - Salesforce includes first touch, last touch and even split models.
  - You can create custom models. Some teams load their own percentages from another tool.
  - Campaign Influence reports show influenced pipeline and revenue by campaign under each model.

## In HubSpot

HubSpot has attribution reports in its higher tiers (check your subscription):
- **Contact create attribution:** which interactions led to new contacts.
- **Deal create attribution:** which interactions led to new deals.
- **Revenue attribution:** which interactions influenced closed-won revenue.

Models HubSpot currently lists include first touch, last touch, linear, time decay and an **Empirical** model, which weights touches based on your own past conversion paths. HubSpot's help docs say Empirical replaces its older U-shaped and W-shaped models, though many guides still mention them. Check what your account shows.

If HubSpot syncs with Salesforce, decide which system is the source of truth for attribution. Deals, contacts and campaign data can differ between the two after sync.

## Self-reported attribution

Add a field to high-intent forms like "Contact us" or a demo request: **"How did you hear about us?"** Use a short picklist plus "Other."
- It catches what tracking misses: podcasts, word of mouth, a LinkedIn post someone shared, a colleague's recommendation.
- Compare it with software attribution. Big gaps tell you where tracking is weak.
- Treat it as directional. People forget and pick the first option.

## Beyond touch-based attribution

Touch-based models only see clicks and records in your systems. They can't see whether a deal would have happened anyway. For bigger budget decisions, larger teams also use:
- **Holdout or incrementality tests:** don't show ads to a set of target accounts and compare the results.
- **Marketing mix modeling:** a statistical model of spend vs. results over time.

These are worth knowing about, but most B2B teams should get the CRM chain in Parts 1–5 working first.

## Sources
- [Salesforce Ben: Campaign Influence, a marketer's guide](https://www.salesforceben.com/salesforce-campaign-influence-marketers-guide/)
- [How Customizable Campaign Influence works (Tectonic)](https://gettectonic.com/customizable-campaign-influence/)
- [HubSpot Knowledge Base: Create attribution reports](https://knowledge.hubspot.com/reports/create-attribution-reports)
- [HubSpot: A closer look at attribution models](https://blog.hubspot.com/customers/a-closer-look-at-attribution-models-in-hubspot)
