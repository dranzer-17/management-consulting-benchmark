-- Defense share of federal contract value (Set 2)
SELECT f.firm_name,
       ROUND(100.0 * SUM(CASE WHEN a.agency = 'Department of Defense' THEN a.award_usd ELSE 0 END) / SUM(a.award_usd), 1) AS defense_pct,
       COUNT(DISTINCT a.agency) AS agencies
FROM fact_award a JOIN dim_firm f USING (firm_id)
WHERE a.fiscal_year BETWEEN 2015 AND 2024 AND a.award_usd > 0
GROUP BY f.firm_name;
