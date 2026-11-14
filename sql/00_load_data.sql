-- Loads the sample CSVs into a SQLite database.
-- Run from the repo root:  sqlite3 attribution.db < sql/00_load_data.sql
-- Blank CSV cells load as empty strings, so later queries use NULLIF(col, '') to treat them as missing.
.mode csv
.import --csv data/accounts.csv accounts
.import --csv data/campaigns.csv campaigns
.import --csv data/contacts.csv contacts
.import --csv data/leads.csv leads
.import --csv data/campaign_members.csv campaign_members
.import --csv data/opportunities.csv opportunities
.import --csv data/opportunity_contact_roles.csv opportunity_contact_roles

-- Settings used by the influence queries. Change the window to match your org.
CREATE TABLE settings (influence_window_days INTEGER);
INSERT INTO settings VALUES (180);

-- Every campaign touch that should count as influence on a deal:
-- the contact has a contact role on the opportunity, is a responded member of the campaign,
-- and responded on or before the deal was created, within the influence window.
CREATE VIEW influence_links AS
SELECT
  o.opportunity_id,
  o.opportunity_name,
  CAST(o.amount AS REAL)  AS amount,
  o.created_date          AS opp_created_date,
  cm.campaign_id,
  c.campaign_name,
  c.channel,
  cm.contact_id,
  cm.status,
  cm.responded_date
FROM opportunities o
JOIN opportunity_contact_roles ocr ON ocr.opportunity_id = o.opportunity_id
JOIN campaign_members cm           ON cm.contact_id = ocr.contact_id
JOIN campaigns c                   ON c.campaign_id = cm.campaign_id
CROSS JOIN settings s
WHERE cm.is_responded = 'Y'
  AND julianday(cm.responded_date) <= julianday(o.created_date)
  AND julianday(o.created_date) - julianday(cm.responded_date) <= s.influence_window_days;
