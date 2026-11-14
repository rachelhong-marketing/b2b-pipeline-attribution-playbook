-- Part 5: sourced vs. influenced pipeline.
-- Run after 00_load_data.sql:  sqlite3 -header -column attribution.db < sql/01_sourced_vs_influenced.sql

-- 1. Sourced pipeline: one campaign (Primary Campaign Source) gets 100% of each deal.
--    Deals with no primary campaign are counted as sales sourced. These rows add up to total pipeline.
SELECT
  COALESCE(c.campaign_name, '(none: sales sourced)') AS primary_campaign,
  COUNT(*)                                           AS deals,
  SUM(CAST(o.amount AS REAL))                        AS sourced_pipeline
FROM opportunities o
LEFT JOIN campaigns c ON c.campaign_id = NULLIF(o.primary_campaign_id, '')
GROUP BY primary_campaign
ORDER BY sourced_pipeline DESC;

-- 2. Influenced pipeline by campaign: every campaign a buyer on the deal engaged with.
--    One deal can appear under several campaigns, so do NOT add these rows together.
SELECT
  campaign_name,
  COUNT(DISTINCT opportunity_id) AS deals_influenced,
  SUM(amount)                    AS influenced_pipeline
FROM (SELECT DISTINCT opportunity_id, campaign_name, amount FROM influence_links)
GROUP BY campaign_name
ORDER BY influenced_pipeline DESC;

-- 3. Deal by deal: sourced by whom, and influenced by how many campaigns.
SELECT
  o.opportunity_name,
  o.amount,
  CASE WHEN NULLIF(o.primary_campaign_id, '') IS NULL THEN 'Sales sourced' ELSE 'Marketing sourced' END AS sourced,
  (SELECT COUNT(DISTINCT il.campaign_id) FROM influence_links il WHERE il.opportunity_id = o.opportunity_id) AS campaigns_influencing,
  (SELECT COUNT(*) FROM opportunity_contact_roles r WHERE r.opportunity_id = o.opportunity_id)              AS contact_roles
FROM opportunities o
ORDER BY o.opportunity_id;

-- 4. Headline numbers for a leadership report.
SELECT
  ROUND(100.0 * SUM(CASE WHEN NULLIF(primary_campaign_id, '') IS NOT NULL THEN CAST(amount AS REAL) END)
        / SUM(CAST(amount AS REAL)), 1)                                               AS pct_pipeline_marketing_sourced,
  ROUND(100.0 * (SELECT COUNT(DISTINCT opportunity_id) FROM influence_links) / COUNT(*), 1) AS pct_deals_marketing_influenced
FROM opportunities;
