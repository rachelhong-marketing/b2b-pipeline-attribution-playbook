-- Part 7: monthly data audit. Checks 1-7 list records that break the attribution chain; check 8 tests for inflated influence.
-- Run after 00_load_data.sql:  sqlite3 -header -column attribution.db < sql/03_data_audit.sql

-- 1. Opportunities with no contact roles: campaign influence can't link to them.
SELECT o.opportunity_id, o.opportunity_name, o.stage, o.amount
FROM opportunities o
LEFT JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
WHERE r.opportunity_id IS NULL;

-- 2. Unconverted leads at companies with open deals: their touches never reach the deal.
--    Matched on email domain = account website domain (see Part 3).
SELECT l.lead_id, l.full_name, l.company, l.status, o.opportunity_name, o.stage
FROM leads l
JOIN accounts a       ON a.website_domain = substr(l.email, instr(l.email, '@') + 1)
JOIN opportunities o  ON o.account_id = a.account_id AND o.is_closed = 'N'
WHERE l.is_converted = 'N';

-- 3. Contacts who engaged with campaigns but aren't on their account's open deal.
SELECT DISTINCT k.contact_id, k.full_name, a.account_name, o.opportunity_name
FROM contacts k
JOIN accounts a          ON a.account_id = k.account_id
JOIN opportunities o     ON o.account_id = k.account_id AND o.is_closed = 'N'
JOIN campaign_members cm ON cm.contact_id = k.contact_id AND cm.is_responded = 'Y'
LEFT JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id AND r.contact_id = k.contact_id
WHERE r.contact_id IS NULL;

-- 4. Leads with no lead source.
SELECT lead_id, full_name, company, created_date
FROM leads
WHERE NULLIF(lead_source, '') IS NULL;

-- 5. Possible duplicates: more than one lead with the same email.
SELECT email, COUNT(*) AS lead_records, GROUP_CONCAT(lead_id) AS lead_ids
FROM leads
GROUP BY email
HAVING COUNT(*) > 1;

-- 6. Paid search leads with no GCLID saved: can't be sent back to Google Ads (see Part 8).
SELECT lead_id, full_name, lead_source, utm_source, created_date
FROM leads
WHERE lead_source = 'Paid Search' AND NULLIF(gclid, '') IS NULL;

-- 7. Touches left out by the influence window: responded too long before the deal was created.
SELECT o.opportunity_name, cm.campaign_id, cm.contact_id, cm.responded_date, o.created_date
FROM opportunities o
JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
JOIN campaign_members cm         ON cm.contact_id = r.contact_id AND cm.is_responded = 'Y'
CROSS JOIN settings s
WHERE julianday(o.created_date) - julianday(cm.responded_date) > s.influence_window_days;

-- 8. Influence inflation check: what the influence numbers look like if every campaign member counts,
--    including people who were only sent or received an email, vs. only members who responded.
--    If "all members" is much higher, the campaign influence report is overstating marketing's impact.
WITH all_members AS (
  SELECT DISTINCT o.opportunity_id, cm.campaign_id, CAST(o.amount AS REAL) AS amount
  FROM opportunities o
  JOIN opportunity_contact_roles r ON r.opportunity_id = o.opportunity_id
  JOIN campaign_members cm         ON cm.contact_id = r.contact_id
  CROSS JOIN settings s
  WHERE julianday(cm.responded_date) <= julianday(o.created_date)
    AND julianday(o.created_date) - julianday(cm.responded_date) <= s.influence_window_days
),
responded AS (
  SELECT DISTINCT opportunity_id, campaign_id, amount FROM influence_links
)
SELECT
  c.campaign_name,
  (SELECT COUNT(*) FROM all_members a WHERE a.campaign_id = c.campaign_id)               AS deals_all_members,
  (SELECT COALESCE(SUM(amount),0) FROM all_members a WHERE a.campaign_id = c.campaign_id) AS pipeline_all_members,
  (SELECT COUNT(*) FROM responded r WHERE r.campaign_id = c.campaign_id)                 AS deals_responded_only,
  (SELECT COALESCE(SUM(amount),0) FROM responded r WHERE r.campaign_id = c.campaign_id)  AS pipeline_responded_only
FROM campaigns c
ORDER BY pipeline_all_members DESC;
