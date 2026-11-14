# Part 8: Close the loop with ad platforms

By default, ad platforms optimize toward whatever conversion you give them, usually a form fill. In B2B, many form fills never become qualified leads. If the platform only sees form fills, it will find more people like those who fill out forms, not people who become pipeline.

Closing the loop means sending CRM results back to the ad platform, so it can learn which clicks became MQLs, SALs and opportunities.

## How it works with Google Ads

1. **Capture the click ID.** When someone clicks a Google ad, the URL includes a **GCLID**. A hidden form field saves it on the lead (see [Part 2](02-capture-the-source.md)).
2. **Keep it on the record.** The GCLID must sync from the marketing automation tool to the CRM and stay there when the lead converts to a contact.
3. **Send stage changes back.** When the lead reaches MQL, SAL or opportunity, send that event to Google Ads with the GCLID and the date, as an **offline conversion**. Options include Google's built-in Salesforce connection, a scheduled file upload, or a connector tool.
4. **Use it for bidding.** Once enough offline conversions come in, set them as the primary conversion goal, or give them more value than form fills. Smart Bidding then optimizes toward quality.

**Timing matters.** Google keeps a GCLID for 90 days, so conversions uploaded later than that won't count. Set up the sync to run often, not quarterly.

**Newer option: enhanced conversions for leads.** Instead of relying only on the GCLID, you send a hashed (scrambled) version of the email address from the form, and Google matches it to the ad click. Google still recommends sending the GCLID too. Google is also moving offline conversion uploads to a new API (the Data Manager API), so check which upload method your account uses.

## LinkedIn and others

LinkedIn supports offline conversions too: upload a CSV of conversions, connect your CRM, or use LinkedIn's Conversions API. With a CRM connection, LinkedIn can create conversions for stages like leads and qualified leads. Same idea as Google: capture who converted, keep it in the CRM, and send stage changes back.

## Privacy and consent

- Only send data your privacy policy and consent settings allow.
- Customer Match and offline conversion uploads should only use data people gave you directly, like a form fill, not purchased lists.

## Before you move on

- [ ] GCLID (and other click IDs) are saved on leads and kept after conversion.
- [ ] MQL, SAL and opportunity events are sent back to Google Ads on a regular schedule.
- [ ] The team has agreed which conversion the platform should bid toward, and when to switch from form fills.
- [ ] The data sent matches your consent and privacy rules.

## Sources
- [Google Ads Help: Guidelines for importing offline conversions](https://support.google.com/google-ads/answer/15081888)
- [Google Ads Help: Offline conversion imports FAQs](https://support.google.com/google-ads/answer/10029210)
- [Google Ads Help: About enhanced conversions for leads](https://support.google.com/google-ads/answer/15713840)
- [Google Ads Help: Fix discrepancies in offline conversion imports](https://support.google.com/google-ads/answer/13321563)
- [LinkedIn Help: Get started with conversion tracking](https://www.linkedin.com/help/lms/answer/67513)
- [LinkedIn Help: Upload a conversion data CSV file](https://www.linkedin.com/help/lms/answer/a796520)
