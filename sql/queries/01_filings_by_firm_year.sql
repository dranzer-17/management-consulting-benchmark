-- Certified filings and positions per firm and fiscal year (Set 1)
SELECT f.firm_name, l.fiscal_year, COUNT(*) AS certified_filings, SUM(l.positions) AS positions
FROM fact_lca l JOIN dim_firm f USING (firm_id)
WHERE l.certified = 1 AND l.fiscal_year BETWEEN 2015 AND 2025
GROUP BY f.firm_name, l.fiscal_year
ORDER BY f.firm_name, l.fiscal_year;
