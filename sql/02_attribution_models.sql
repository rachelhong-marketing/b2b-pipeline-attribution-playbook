-- Part 6: the same deals under three attribution models.
-- Run after 00_load_data.sql:  sqlite3 -header -column attribution.db < sql/02_attribution_models.sql
-- Credit is split across campaigns linked through influence_links (see 00_load_data.sql).
-- Deals with no influence links (for example, no contact roles) get no credit under any model.

WITH ranked AS (
  SELECT
    opportunity_id,
    campaign_name,
    amount,
    responded_date,
    ROW_NUMBER() OVER (PARTITION BY opportunity_id ORDER BY responded_date ASC,  campaign_id) AS first_rank,
    ROW_NUMBER() OVER (PARTITION BY opportunity_id ORDER BY responded_date DESC, campaign_id) AS last_rank,
    COUNT(*)     OVER (PARTITION BY opportunity_id)                                           AS touches
  FROM influence_links
)
SELECT
  campaign_name,
  SUM(CASE WHEN first_rank = 1 THEN amount ELSE 0 END)   AS first_touch,
  SUM(CASE WHEN last_rank  = 1 THEN amount ELSE 0 END)   AS last_touch,
  ROUND(SUM(amount * 1.0 / touches), 0)                  AS even_split
FROM ranked
GROUP BY campaign_name
ORDER BY even_split DESC;

-- Note: even split here divides each deal by its number of touches, so a campaign touched twice
-- on the same deal gets two shares. Some teams split by distinct campaign instead. Pick one and document it.
