# Part 2: Capture the source

Attribution starts the moment a lead is created. If the source isn't saved then, no report can recover it later.

## 1. Standardize the lead source field

Every lead in Salesforce has a **Lead Source** field. It's the simplest answer to "where did this person come from?"
- Use one fixed picklist, such as Paid Search, Paid Social, Organic Search, Email, Event, Webinar, Content Syndication, Referral, Partner or Sales Prospecting.
- Don't allow free text. "LinkedIn," "linkedin ads" and "LI" become three different sources in a report.
- Set the value automatically from the form or list upload, not by hand.
- Keep the original value. Many teams add an **Original Lead Source** field that's never overwritten, because later activity can change Lead Source.

## 2. Save UTMs and click IDs on the record

Lead Source is broad, like "Paid Social." UTMs tell you which ad and campaign.
- Add custom fields for UTM source, medium, campaign and content, plus **GCLID** for Google Ads clicks.
- Capture them with **hidden fields** on your forms. HubSpot, Eloqua and Account Engagement forms can all read values from the page URL and pass them into the record without the visitor seeing anything.
- Make sure they **sync to the CRM**. A common break is UTMs saved in the marketing automation tool but never mapped to Salesforce fields.
- Agree on one naming pattern for UTMs across every team that runs ads. For a full UTM naming convention, see [B2B Paid Media Playbook: UTM naming](https://github.com/rachelhong-marketing/b2b-paid-media-playbook/blob/main/tracking/utm-naming-convention.md).

## 3. Set up campaigns that match how you report

A **campaign** in Salesforce is any program you want credit for: a webinar, an event, a paid search program, an email nurture, a content syndication buy.
- **Naming:** use one pattern, such as year, quarter, type and name: `2026-Q1-Webinar-Measuring-Media`.
- **Hierarchy:** group campaigns under parents, like by product or quarterly theme, so results roll up. A three-level example is in [B2B Paid Media Playbook: Salesforce campaign hierarchy](https://github.com/rachelhong-marketing/b2b-paid-media-playbook/blob/main/tracking/salesforce-campaign-hierarchy.md).
- **Cost:** enter actual cost on the campaign so you can calculate cost per lead and cost per MQL later.
- **Type and channel:** fill these in the same way every time. They're what you group by in reports.

## 4. Add every person who engaged as a campaign member

A person becomes a **campaign member** when they engage with a campaign. A lead or contact can be a member of many campaigns, which is what makes multi-touch attribution possible.
- **Set member statuses that show the level of engagement**, such as Registered → Attended for webinars, or Visited booth → Meeting held for events.
- **Mark which statuses count as a real response.** Opening an email may not count, but downloading a guide does.
- **Scoring:** if your MQL rule includes engagement, give points by member status (see [Part 1](01-define-the-funnel.md)).
- **Keep the date of the response.** It's needed later to decide whether the touch happened before the deal was created.

## Before you move on

- [ ] Lead Source uses a fixed picklist, and Original Lead Source is never overwritten.
- [ ] UTM and GCLID fields exist in the CRM and fill in from hidden form fields.
- [ ] Campaigns follow one naming pattern, with type, channel and cost filled in.
- [ ] Every engaged person is added as a campaign member with a status and response date.
- [ ] Offline lists (events, partner leads) are uploaded into a campaign, not just imported as leads.

## Sources
- [Salesforce Ben: Lead Source vs. Campaign, which to use when](https://www.salesforceben.com/salesforce-lead-source-vs-campaign-which-to-use-when/)
- [Salesforce Ben: Salesforce marketing attribution guide](https://salesforceben.com/comprehensive-guide-to-salesforce-marketing-attribution-in-2025)
