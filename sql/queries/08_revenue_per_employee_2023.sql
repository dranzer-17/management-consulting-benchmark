-- 2023 revenue per employee, with data type so estimates are visible (Set 3)
SELECT f.firm_name,
       r.value AS revenue_usd_bn, h.value AS headcount,
       ROUND(r.value * 1e9 / h.value / 1e3) AS revenue_per_employee_usd_k,
       r.type AS revenue_basis, h.type AS headcount_basis
FROM fact_firm_scale r
JOIN fact_firm_scale h ON h.firm_id = r.firm_id AND h.year = r.year AND h.metric = 'headcount'
JOIN dim_firm f ON f.firm_id = r.firm_id
WHERE r.metric = 'revenue' AND r.year = 2023;
