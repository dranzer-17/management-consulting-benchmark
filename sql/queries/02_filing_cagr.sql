-- Filing CAGR FY2016 to FY2024 (Set 1)
WITH y AS (
    SELECT firm_id, fiscal_year, COUNT(*) AS n
    FROM fact_lca WHERE certified = 1 AND fiscal_year IN (2016, 2024)
    GROUP BY firm_id, fiscal_year)
SELECT f.firm_name,
       a.n AS fy2016, b.n AS fy2024,
       ROUND(100.0 * (POWER(1.0 * b.n / a.n, 1.0 / 8) - 1), 1) AS cagr_pct
FROM y a JOIN y b ON a.firm_id = b.firm_id AND a.fiscal_year = 2016 AND b.fiscal_year = 2024
JOIN dim_firm f ON f.firm_id = a.firm_id;
