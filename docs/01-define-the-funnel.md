# Part 1: Define the funnel first

You can't measure what marketing contributed until sales and marketing agree on what each stage means. Do this before building any report. The first thing to find out at a new company is how it defines an MQL.

## The stages

| Stage | What it means | Who usually owns it |
|---|---|---|
| **Lead** | A person we have contact details for, from any source: a form fill, an event list, a content syndication partner | Marketing |
| **MQL** (marketing qualified lead) | A lead that meets the company's MQL rules (see below) | Marketing |
| **SAL** (sales accepted lead) | Sales has reviewed the MQL and agreed to follow up | Sales development |
| **SQL** (sales qualified lead) | Sales has confirmed a real need, budget or timing, and is ready to open a deal | Sales |
| **Opportunity** | A deal record in the CRM with an amount and a stage | Sales |

Names vary. Some companies skip SAL, and some use "inquiry" instead of "lead." What matters is that everyone uses the same definitions and the CRM records the date each stage was reached.

## How companies define an MQL

There's no standard definition. The two most common approaches are:

**1. Fit only**
- The lead is the right company (industry, size, region, or on the target account list) and the right person (job title, seniority, department).
- Simple to explain and easy to set up.
- The risk: a perfect-fit person who downloaded one guide a year ago counts the same as one asking for a demo.

**2. Fit + engagement**
- The lead must pass fit **and** reach an engagement score.
- Fit says "this person could buy." Engagement says "this person is showing interest now."
- Engagement points usually come from activity: content downloads, webinar attendance, event visits, email clicks, pricing or product page visits, and demo requests.

A demo or "contact us" request is usually treated as an MQL right away if the person fits, because it shows clear intent.

## Lead scoring: where to do it

**Recommended: in the marketing automation tool**, such as HubSpot, Eloqua or Marketing Cloud Account Engagement (formerly Pardot).
- That's where email, web and form activity is captured, so engagement points can be added as soon as something happens.
- Fit and engagement scores can be set up as separate scores, so you can see why someone became an MQL.
- The score and MQL date then sync to the CRM.

**Option: inside Salesforce**, with Einstein Lead Scoring. It uses machine learning on your past conversions to score leads. It can work well with enough history, but it's harder to explain why a lead scored high. It also only sees activity that reaches the CRM.

## Scoring engagement from campaigns

If your MQL counts engagement with events or content, track it at the **campaign member** level:
- Each campaign (a webinar, an event, a content offer) has member statuses for each step, such as "Registered," "Attended," "Visited booth" or "Downloaded."
- Points are given by status. Attending a webinar is worth more than registering for one.
- This keeps scoring consistent across campaigns and makes it easy to report which campaigns produced MQLs.

See the example scoring sheet in [templates/lead-scoring-template.csv](../templates/lead-scoring-template.csv). The points are made up to show the idea. Set your own based on which actions have led to deals in the past.

## Before you move on

- [ ] Every stage has a written definition both sales and marketing agreed to.
- [ ] The CRM stores the date each stage was reached (MQL date, SAL date, and so on).
- [ ] The MQL rule (fit only, or fit + engagement) is written down, including scoring thresholds.
- [ ] There's a process for MQLs that sales rejects, so they go back to nurture instead of disappearing.

Template: [templates/funnel-definitions.md](../templates/funnel-definitions.md)

## Sources
- [Trailhead: Einstein scoring in Account Engagement](https://trailhead.salesforce.com/content/learn/modules/lead-scoring-and-grading-in-account-engagement/einstein-scoring-in-account-engagement)
- [How Salesforce Einstein Lead Scoring works (CRM Science)](https://www.crmscience.com/single-post/how-salesforce-einstein-lead-scoring-works)
- [Salesforce Ben: Salesforce marketing attribution guide](https://salesforceben.com/comprehensive-guide-to-salesforce-marketing-attribution-in-2025)
