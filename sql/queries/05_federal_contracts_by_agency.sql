-- Federal contract value by firm and agency, FY2015 to FY2024, excluding zero-value awards (Set 2)
SELECT f.firm_name, a.agency, COUNT(*) AS awards, ROUND(SUM(a.award_usd) / 1e6, 1) AS value_usd_m
FROM fact_award a JOIN dim_firm f USING (firm_id)
WHERE a.fiscal_year BETWEEN 2015 AND 2024 AND a.award_usd > 0
GROUP BY f.firm_name, a.agency
ORDER BY f.firm_name, value_usd_m DESC;
