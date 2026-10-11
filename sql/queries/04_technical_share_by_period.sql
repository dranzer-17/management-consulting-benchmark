-- Share of certified filings in technical occupations, two periods (Set 4)
SELECT f.firm_name,
       ROUND(100.0 * AVG(CASE WHEN l.fiscal_year BETWEEN 2015 AND 2019 THEN l.is_technical END), 1) AS tech_pct_fy2015_19,
       ROUND(100.0 * AVG(CASE WHEN l.fiscal_year BETWEEN 2021 AND 2025 THEN l.is_technical END), 1) AS tech_pct_fy2021_25
FROM fact_lca l JOIN dim_firm f USING (firm_id)
WHERE l.certified = 1
GROUP BY f.firm_name;
